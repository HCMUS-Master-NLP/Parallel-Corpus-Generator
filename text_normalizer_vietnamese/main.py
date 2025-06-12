"""
Main CLI Entry Point - Folder Processing Edition
"""

import argparse
import sys
import traceback
from pathlib import Path

from text_cleaner import TextCleaner
from file_processor import FileProcessor
from statistics import StatisticsReporter
from exceptions import ConfigurationError, DictionaryError, FileProcessingError


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Vietnamese OCR Text Cleaner - Folder Processing Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s input_folder output_folder
            %(prog)s input_folder output_folder -c patterns.json -v
            %(prog)s input_folder output_folder -d QuocNgu_SinoNom_Dic.json --verbose
            %(prog)s input_folder output_folder -c patterns.json -d dictionary.json -v -ru
            %(prog)s input_folder output_folder --extensions .txt .md --recursive
        """
    )

    # Positional arguments
    parser.add_argument(
        'input_folder', help='Input folder containing text files to process')
    parser.add_argument(
        'output_folder', help='Output folder for cleaned text files')

    # Optional arguments
    parser.add_argument('-c', '--config', type=Path,
                        help='JSON file with noise patterns (optional)')
    parser.add_argument('-d', '--dictionary', type=Path,
                        help='Vietnamese dictionary JSON file (optional)')
    parser.add_argument('-e', '--encoding', default='utf-8',
                        help='Text file encoding (default: utf-8)')
    parser.add_argument('--extensions', nargs='+', default=['.txt'],
                        help='File extensions to process (default: .txt)')
    parser.add_argument('--recursive', '-r', action='store_true',
                        help='Process files recursively in subdirectories')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')

    return parser


def progress_callback(current: int, total: int, filename: str, original_len: int, cleaned_len: int, reduction: float):
    """Callback function for progress updates during processing."""
    print(f"Progress: {current}/{total} - Processed '{filename}' "
          f"({original_len:,} → {cleaned_len:,} chars, {reduction:.1f}% reduction)")


def main() -> None:
    """Main entry point with comprehensive error handling for folder processing."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Convert string paths to Path objects
    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder)

    # Validate input folder
    if not input_folder.exists():
        print(
            f"Error: Input folder '{input_folder}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not input_folder.is_dir():
        print(f"Error: '{input_folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize components
        cleaner = TextCleaner(
            config_path=args.config,
            dictionary_path=args.dictionary,
            verbose=args.verbose
        )
        processor = FileProcessor(encoding=args.encoding)
        reporter = StatisticsReporter()

        # Set up progress callback for verbose mode
        callback = progress_callback if args.verbose else None

        print(f"Starting folder processing...")
        print(f"Input folder: {input_folder}")
        print(f"Output folder: {output_folder}")
        print(f"Extensions: {args.extensions}")
        print(f"Recursive: {args.recursive}")

        # Process the entire folder
        file_statistics, total_original_length, total_cleaned_length, failed_files = processor.process_folder(
            input_folder=input_folder,
            output_folder=output_folder,
            cleaner=cleaner,
            extensions=args.extensions,
            recursive=args.recursive,
            verbose=args.verbose,
            progress_callback=callback
        )

        # Generate reports
        reporter.generate_report(file_statistics, total_original_length,
                                 total_cleaned_length, output_folder, failed_files, input_folder)

        if args.verbose and file_statistics:
            reporter.generate_detailed_report(
                file_statistics, total_original_length, total_cleaned_length, show_chart=True)

        sys.exit(0)

    except (ConfigurationError, DictionaryError) as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    except FileProcessingError as e:
        print(f"File Processing Error: {e}", file=sys.stderr)
        sys.exit(2)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
