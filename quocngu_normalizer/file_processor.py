"""File I/O operations for text processing."""

from pathlib import Path
from typing import Dict, Tuple, List
import sys

from quocngu_normalizer.cleaning_config import LoggerMixin
from quocngu_normalizer.exceptions import FileProcessingError, TextCleanerError


class FileProcessor(LoggerMixin):
    """Handles file I/O operations for text processing with robust error handling."""

    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(logger_name=self.__class__.__name__)
        self.encoding = encoding

    def read_file(self, file_path: Path) -> str:
        """Read text from file with comprehensive error handling."""
        if not file_path.exists():
            raise FileProcessingError(f"Input file not found: {file_path}")

        if not file_path.is_file():
            raise FileProcessingError(f"Path is not a file: {file_path}")

        try:
            with file_path.open('r', encoding=self.encoding) as f:
                content = f.read()

            self.logger.info(
                "Successfully read %d characters from %s", len(content), file_path)
            return content

        except UnicodeDecodeError as e:
            raise FileProcessingError(
                f"Failed to decode file {file_path} with {self.encoding}: {e}")
        except IOError as e:
            raise FileProcessingError(f"Failed to read file {file_path}: {e}")

    def write_file(self, file_path: Path, content: str) -> None:
        """Write text to file with error handling and directory creation."""
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open('w', encoding=self.encoding) as f:
                f.write(content)

            self.logger.info(
                "Successfully wrote %d characters to %s", len(content), file_path)

        except IOError as e:
            raise FileProcessingError(f"Failed to write file {file_path}: {e}")

    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        cleaner,  # TextCleaner - avoiding circular import
    ) -> Tuple[int, int, Dict[str, int]]:
        """Process a single file through the cleaning pipeline."""
        try:
            # Read input
            original_text = self.read_file(input_path)
            original_length = len(original_text)

            # Clean text
            cleaned_text = cleaner.clean_text(
                original_text)
            cleaned_length = len(cleaned_text)

            # Write output
            self.write_file(output_path, cleaned_text)

            # Calculate statistics
            reduction_percent = ((original_length - cleaned_length) /
                                 original_length * 100) if original_length > 0 else 0

            self.logger.info(
                "Processing complete: %.1f%% size reduction", reduction_percent)

            return original_length, cleaned_length, cleaner.get_cleaning_stats()

        except (TextCleanerError, FileProcessingError) as e:
            raise FileProcessingError(f"File processing failed: {e}")

    def find_text_files(self, input_folder: Path, extensions: List[str], recursive: bool = False) -> List[Path]:
        """Find all text files in the input folder with specified extensions."""
        if not input_folder.exists():
            raise FileProcessingError(
                f"Input folder not found: {input_folder}")

        if not input_folder.is_dir():
            raise FileProcessingError(
                f"Path is not a directory: {input_folder}")

        text_files = []

        # Normalize extensions to ensure they start with a dot
        normalized_extensions = [ext if ext.startswith(
            '.') else f'.{ext}' for ext in extensions]

        try:
            if recursive:
                # Use rglob for recursive search
                for ext in normalized_extensions:
                    text_files.extend(input_folder.rglob(f'*{ext}'))
            else:
                # Use glob for non-recursive search
                for ext in normalized_extensions:
                    text_files.extend(input_folder.glob(f'*{ext}'))

            sorted_files = sorted(text_files)
            self.logger.info("Found %d files with extensions %s in %s",
                             len(sorted_files), extensions, input_folder)

            return sorted_files

        except Exception as e:
            raise FileProcessingError(
                f"Failed to search for files in {input_folder}: {e}")

    def get_relative_output_path(self, input_file: Path, input_folder: Path, output_folder: Path) -> Path:
        """Get the corresponding output path for an input file, maintaining directory structure."""
        try:
            relative_path = input_file.relative_to(input_folder)
            return output_folder / relative_path
        except ValueError as e:
            raise FileProcessingError(
                f"Input file {input_file} is not relative to {input_folder}: {e}")

    def process_folder(
        self,
        input_folder: Path,
        output_folder: Path,
        cleaner,  # TextCleaner - avoiding circular import
        extensions: List[str] = ['.txt'],
        recursive: bool = False,
        verbose: bool = False,
        progress_callback=None
    ) -> Tuple[List[Dict], int, int, List[Dict]]:
        """
        Process all text files in a folder through the cleaning pipeline.

        Returns:
            Tuple of (file_statistics, total_original_length, total_cleaned_length, failed_files)
        """
        # Find all text files to process
        text_files = self.find_text_files(input_folder, extensions, recursive)

        if not text_files:
            self.logger.warning(
                "No files found with extensions %s in %s", extensions, input_folder)
            return [], 0, 0, []

        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)

        # Process all files
        file_statistics = []
        total_original_length = 0
        total_cleaned_length = 0
        successful_files = 0
        failed_files = []

        self.logger.info(
            "Starting batch processing of %d files", len(text_files))

        for i, input_file in enumerate(text_files, 1):
            try:
                # Determine output path (maintain directory structure)
                output_file = self.get_relative_output_path(
                    input_file, input_folder, output_folder)

                # Ensure output directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)

                # Process file
                original_len, cleaned_len, stats = self.process_file(
                    input_path=input_file,
                    output_path=output_file,
                    cleaner=cleaner,
                )

                # Calculate reduction percentage
                reduction = ((original_len - cleaned_len) /
                             original_len * 100) if original_len > 0 else 0

                # Store statistics
                file_stat = {
                    'filename': input_file.name,
                    'input_path': str(input_file),
                    'output_path': str(output_file),
                    'original_length': original_len,
                    'cleaned_length': cleaned_len,
                    'reduction_percent': reduction,
                    'detailed_stats': stats
                }
                file_statistics.append(file_stat)

                total_original_length += original_len
                total_cleaned_length += cleaned_len
                successful_files += 1

                # Progress callback
                if progress_callback:
                    progress_callback(
                        i, len(text_files), input_file.name, original_len, cleaned_len, reduction)

                # Progress indication for verbose mode
                if verbose or (i % 10 == 0) or i == len(text_files):
                    self.logger.info("Progress: %d/%d - Processed '%s' (%s → %s chars, %.1f%% reduction)",
                                     i, len(text_files), input_file.name,
                                     f"{original_len:,}", f"{cleaned_len:,}", reduction)

            except FileProcessingError as e:
                error_msg = f"Failed to process '{input_file}': {e}"
                self.logger.error(error_msg)
                failed_files.append({'file': str(input_file), 'error': str(e)})

                # Print warning to stderr for immediate feedback
                print(f"Warning: {error_msg}", file=sys.stderr)
                continue

        self.logger.info("Batch processing complete: %d/%d files successful",
                         successful_files, len(text_files))

        if failed_files:
            self.logger.warning(
                "Failed to process %d files", len(failed_files))

        return file_statistics, total_original_length, total_cleaned_length, failed_files
