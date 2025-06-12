#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import os
import glob
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


def split_sentences_chunk(text_chunk):
    """
    Split a chunk of Vietnamese text into sentences.
    Uses regex to identify sentence boundaries based on punctuation marks.
    """
    if not text_chunk.strip():
        return []

    # Remove extra whitespace and normalize the text
    text_chunk = re.sub(r'\s+', ' ', text_chunk.strip())

    # Define sentence ending patterns for Vietnamese text
    sentence_endings = r'[.!?…]+'

    # Split by sentence endings and keep the punctuation
    parts = re.split(f'({sentence_endings})', text_chunk)

    result = []
    current_sentence = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if re.match(f'^{sentence_endings}$', part):
            # This is sentence ending
            current_sentence += part
            if current_sentence.strip():
                result.append(current_sentence.strip())
            current_sentence = ""
        else:
            # This is text
            current_sentence += part

    # Add any remaining sentence
    if current_sentence.strip():
        result.append(current_sentence.strip())

    # Filter out very short sentences (likely fragments)
    result = [s for s in result if len(s.strip()) > 2]

    return result


def split_text_into_chunks(text, num_chunks=None):
    """
    Split text into chunks for parallel processing.
    Try to split at sentence boundaries to avoid breaking sentences.
    """
    if num_chunks is None:
        num_chunks = min(multiprocessing.cpu_count(),
                         20)  # Limit to 20 threads max

    if len(text) < 1000:  # Small text, no need to split
        return [text]

    # Calculate approximate chunk size
    chunk_size = len(text) // num_chunks
    chunks = []

    start = 0
    for i in range(num_chunks - 1):
        # Find a good breaking point (end of sentence)
        end = start + chunk_size

        # Look for sentence endings within reasonable distance
        search_range = min(chunk_size // 4, 500)  # Don't search too far
        best_break = end

        for j in range(max(0, end - search_range), min(len(text), end + search_range)):
            if text[j] in '.!?…':
                # Found a sentence ending, check if it's followed by space or end
                if j + 1 >= len(text) or text[j + 1].isspace():
                    best_break = j + 1
                    break

        chunks.append(text[start:best_break])
        start = best_break

    # Add the remaining text as the last chunk
    if start < len(text):
        chunks.append(text[start:])

    return [chunk for chunk in chunks if chunk.strip()]


def split_sentences_parallel(text, max_workers=None):
    """
    Split text into sentences using parallel processing.
    """
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 8)

    # Split text into chunks
    chunks = split_text_into_chunks(text, max_workers)

    if len(chunks) <= 1:
        # Small text, process directly
        return split_sentences_chunk(text)

    # Process chunks in parallel
    all_sentences = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all chunks for processing
        future_to_chunk = {executor.submit(split_sentences_chunk, chunk): chunk
                           for chunk in chunks}

        # Collect results in order
        for i, chunk in enumerate(chunks):
            for future in future_to_chunk:
                if future_to_chunk[future] == chunk:
                    try:
                        sentences = future.result()
                        all_sentences.extend(sentences)
                    except Exception as exc:
                        print(
                            f'Chunk {i} generated an exception: {exc}', file=sys.stderr)
                    break

    return all_sentences


def write_text_output(sentences, output_file):
    """Write sentences to text file, one per line."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')


def write_json_output(sentences, output_file):
    """Write sentences to JSON file as a list."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2)


def process_file(input_file_path, output_file_path, max_workers, use_json):
    """Process a single file and save the output."""
    try:
        print(f"Processing: {input_file_path}")

        # Read input file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        print(f"  Input text size: {len(text)} characters")

        # Split into sentences using parallel processing
        sentences = split_sentences_parallel(text, max_workers)

        # Write output
        if use_json:
            write_json_output(sentences, output_file_path)
        else:
            write_text_output(sentences, output_file_path)

        print(
            f"  Successfully split {len(sentences)} sentences to {output_file_path}")
        return True

    except Exception as e:
        print(f"  Error processing {input_file_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Split text files in a folder into sentences using multi-threading')
    parser.add_argument(
        'input_folder', help='Input folder containing text files')
    parser.add_argument(
        'output_folder', help='Output folder for processed files')
    parser.add_argument('--json', action='store_true',
                        help='Output in JSON format as a list of sentences')
    parser.add_argument('--threads', type=int, default=None,
                        help='Number of threads to use (default: auto-detect)')

    args = parser.parse_args()

    try:
        # Check if input folder exists
        if not os.path.isdir(args.input_folder):
            print(
                f"Error: Input folder '{args.input_folder}' not found.", file=sys.stderr)
            sys.exit(1)

        # Create output folder if it doesn't exist
        os.makedirs(args.output_folder, exist_ok=True)

        # Find all text files in input folder
        text_extensions = ['*.txt', '*.text']
        input_files = []

        for extension in text_extensions:
            pattern = os.path.join(args.input_folder, extension)
            input_files.extend(glob.glob(pattern))

        if not input_files:
            print(
                f"No text files found in '{args.input_folder}'", file=sys.stderr)
            print("Looking for files with extensions: .txt, .text", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(input_files)} text file(s) to process")

        # Determine number of threads
        max_workers = args.threads or min(multiprocessing.cpu_count(), 8)
        print(f"Using {max_workers} threads for processing")

        # Process each file
        successful_files = 0
        failed_files = 0

        for input_file_path in input_files:
            # Get the base filename without extension
            base_filename = os.path.splitext(
                os.path.basename(input_file_path))[0]

            # Determine output file extension and path
            if args.json:
                output_filename = f"{base_filename}.json"
            else:
                output_filename = f"{base_filename}.txt"

            output_file_path = os.path.join(
                args.output_folder, output_filename)

            # Process the file
            if process_file(input_file_path, output_file_path, max_workers, args.json):
                successful_files += 1
            else:
                failed_files += 1

        # Print summary
        print(f"\nProcessing complete:")
        print(f"  Successfully processed: {successful_files} files")
        if failed_files > 0:
            print(f"  Failed to process: {failed_files} files")

        output_format = "JSON" if args.json else "text"
        print(f"  Output format: {output_format}")
        print(f"  Output folder: {args.output_folder}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
