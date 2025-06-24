"""
Statistical analysis and reporting for Vietnamese OCR text cleaning.
"""

from typing import List, Dict
from pathlib import Path

# No matplotlib - console reports only
HAS_MATPLOTLIB = False


class StatisticsReporter:
    """Handles statistics calculation and console reporting for text cleaning results."""

    def __init__(self):
        self.has_matplotlib = HAS_MATPLOTLIB

    def _extract_sentence_statistics(self, file_stats: List[Dict]) -> Dict:
        """Extract and aggregate sentence statistics from all processed files."""
        total_original_sentences = 0
        total_cleaned_sentences = 0
        total_original_words = 0
        total_cleaned_words = 0

        files_with_sentences = []
        original_char_lengths = []
        cleaned_char_lengths = []
        original_word_lengths = []
        cleaned_word_lengths = []

        for stat in file_stats:
            detailed_stats = stat.get('detailed_stats', {})

            # Extract sentence counts
            orig_sentences = detailed_stats.get('original_sentences', 0)
            clean_sentences = detailed_stats.get('cleaned_sentences', 0)

            # Extract word counts
            orig_words = detailed_stats.get('original_words', 0)
            clean_words = detailed_stats.get('cleaned_words', 0)

            # Extract average sentence lengths
            orig_char_avg = detailed_stats.get(
                'original_average_sentence_length', 0)
            clean_char_avg = detailed_stats.get(
                'cleaned_average_sentence_length', 0)
            orig_word_avg = detailed_stats.get(
                'original_words_per_sentence', 0)
            clean_word_avg = detailed_stats.get(
                'cleaned_words_per_sentence', 0)

            if orig_sentences > 0:  # Only include files with sentences
                total_original_sentences += orig_sentences
                total_cleaned_sentences += clean_sentences
                total_original_words += orig_words
                total_cleaned_words += clean_words

                files_with_sentences.append({
                    'filename': stat['filename'],
                    'original_sentences': orig_sentences,
                    'cleaned_sentences': clean_sentences,
                    'original_char_avg': orig_char_avg,
                    'cleaned_char_avg': clean_char_avg,
                    'original_word_avg': orig_word_avg,
                    'cleaned_word_avg': clean_word_avg
                })

                if orig_char_avg > 0:
                    original_char_lengths.append(orig_char_avg)
                if clean_char_avg > 0:
                    cleaned_char_lengths.append(clean_char_avg)
                if orig_word_avg > 0:
                    original_word_lengths.append(orig_word_avg)
                if clean_word_avg > 0:
                    cleaned_word_lengths.append(clean_word_avg)

        # Calculate overall averages
        overall_orig_char_avg = sum(
            original_char_lengths) / len(original_char_lengths) if original_char_lengths else 0
        overall_clean_char_avg = sum(
            cleaned_char_lengths) / len(cleaned_char_lengths) if cleaned_char_lengths else 0
        overall_orig_word_avg = sum(
            original_word_lengths) / len(original_word_lengths) if original_word_lengths else 0
        overall_clean_word_avg = sum(
            cleaned_word_lengths) / len(cleaned_word_lengths) if cleaned_word_lengths else 0

        return {
            'total_original_sentences': total_original_sentences,
            'total_cleaned_sentences': total_cleaned_sentences,
            'total_original_words': total_original_words,
            'total_cleaned_words': total_cleaned_words,
            'overall_orig_char_avg': overall_orig_char_avg,
            'overall_clean_char_avg': overall_clean_char_avg,
            'overall_orig_word_avg': overall_orig_word_avg,
            'overall_clean_word_avg': overall_clean_word_avg,
            'files_with_sentences': files_with_sentences,
            'files_count': len(files_with_sentences)
        }

    def generate_report(self, file_stats: List[Dict], total_original: int, total_cleaned: int, output_folder: Path, failed_files: List[Dict] = None, input_folder: Path = None):
        """Generate clean console statistics report."""
        if not file_stats and not failed_files:
            print("No files were processed")
            return

        # Print comprehensive analysis summary
        self._print_comprehensive_analysis(
            file_stats, total_original, total_cleaned)

        # Print detailed results table
        self._print_detailed_results_table(file_stats)

        if failed_files:
            self._print_failed_files_table(failed_files)

    def _print_comprehensive_analysis(self, file_stats: List[Dict], total_original: int, total_cleaned: int):
        """Print comprehensive analysis matching the user's screenshot format."""
        if not file_stats:
            return

        overall_reduction = ((total_original - total_cleaned) /
                             total_original * 100) if total_original > 0 else 0
        sentence_stats = self._extract_sentence_statistics(file_stats)

        # Calculate reduction statistics
        reductions = [stat['reduction_percent'] for stat in file_stats]
        avg_reduction = sum(reductions) / len(reductions) if reductions else 0
        max_reduction = max(reductions) if reductions else 0
        min_reduction = min(reductions) if reductions else 0

        print(f"\n{'='*70}")
        print("PROCESSING ANALYSIS SUMMARY")
        print(f"{'='*70}")

        # FILES & CHARACTERS section
        print(f"\nFILES & CHARACTERS:")
        print(f"   Files Processed: {len(file_stats)}")
        print(
            f"   Total Characters: {total_original:,} → {total_cleaned:,} ({overall_reduction:.1f}%)")
        print(
            f"   Average Reduction: {avg_reduction:.1f}% | Max: {max_reduction:.1f}% | Min: {min_reduction:.1f}%")

        # SENTENCE ANALYSIS section
        if sentence_stats['files_count'] > 0:
            sent_change = ((sentence_stats['total_cleaned_sentences'] - sentence_stats['total_original_sentences']) /
                           sentence_stats['total_original_sentences'] * 100) if sentence_stats['total_original_sentences'] > 0 else 0
            word_change = ((sentence_stats['total_cleaned_words'] - sentence_stats['total_original_words']) /
                           sentence_stats['total_original_words'] * 100) if sentence_stats['total_original_words'] > 0 else 0

            print(f"\nSENTENCE ANALYSIS:")
            print(
                f"   Total Sentences: {sentence_stats['total_original_sentences']:,} → {sentence_stats['total_cleaned_sentences']:,} ({sent_change:+.1f}%)")
            print(
                f"   Total Words: {sentence_stats['total_original_words']:,} → {sentence_stats['total_cleaned_words']:,} ({word_change:+.1f}%)")
            print(
                f"   Avg Chars/Sentence: {sentence_stats['overall_orig_char_avg']:.1f} → {sentence_stats['overall_clean_char_avg']:.1f}")
            print(
                f"   Avg Words/Sentence: {sentence_stats['overall_orig_word_avg']:.1f} → {sentence_stats['overall_clean_word_avg']:.1f}")

    def _print_detailed_results_table(self, file_stats: List[Dict]):
        """Print detailed results table for each file."""
        if not file_stats:
            return

        print(f"\n{'='*100}")
        print(f"DETAILED RESULTS")
        print(f"{'='*100}")

        # All files table - clean and organized
        print(f"{'#':<3} {'Filename':<40} {'Original':<12} {'Cleaned':<12} {'Reduction':<10} {'Sentences':<12}")
        print(f"{'-'*3} {'-'*40} {'-'*12} {'-'*12} {'-'*10} {'-'*12}")

        # Sort by reduction percentage for better insights
        sorted_stats = sorted(
            file_stats, key=lambda x: x['reduction_percent'], reverse=True)

        for i, stat in enumerate(sorted_stats, 1):
            filename = stat['filename'][:37] + \
                "..." if len(stat['filename']) > 40 else stat['filename']

            # Extract sentence info if available
            detailed_stats = stat.get('detailed_stats', {})
            orig_sentences = detailed_stats.get('original_sentences', 0)
            clean_sentences = detailed_stats.get('cleaned_sentences', 0)
            sentence_info = f"{orig_sentences}→{clean_sentences}" if orig_sentences > 0 else "N/A"

            print(f"{i:<3} {filename:<40} {stat['original_length']:>12,} {stat['cleaned_length']:>12,} "
                  f"{stat['reduction_percent']:>9.1f}% {sentence_info:<12}")

    def _print_failed_files_table(self, failed_files: List[Dict]):
        """Print failed files table."""
        print(f"\n{'='*70}")
        print(f"FAILED FILES ({len(failed_files)})")
        print(f"{'='*70}")

        print(f"{'#':<3} {'Filename':<40} {'Error':<25}")
        print(f"{'-'*3} {'-'*40} {'-'*25}")

        for i, failed in enumerate(failed_files, 1):
            filename = failed['file'][:37] + \
                "..." if len(failed['file']) > 40 else failed['file']
            error = failed['error'][:22] + \
                "..." if len(failed['error']) > 25 else failed['error']
            print(f"{i:<3} {filename:<40} {error:<25}")

    def _print_sentence_statistics_table(self, file_stats: List[Dict]):
        """Print sentence and word statistics in tabular format."""
        if not file_stats:
            return

        # Extract sentence statistics
        sentence_stats = self._extract_sentence_statistics(file_stats)

        if sentence_stats['files_count'] == 0:
            print(f"\n{'='*70}")
            print("SENTENCE ANALYSIS")
            print(f"{'='*70}")
            print("No sentence data available for analysis.")
            return

        print(f"\n{'='*70}")
        print("SENTENCE & WORD ANALYSIS")
        print(f"{'='*70}")

        # Overall statistics table
        print(f"{'Metric':<30} {'Original':<15} {'Cleaned':<15} {'Change':<15}")
        print(f"{'-'*30} {'-'*15} {'-'*15} {'-'*15}")

        # Sentence counts
        sent_change = ((sentence_stats['total_cleaned_sentences'] - sentence_stats['total_original_sentences']) /
                       sentence_stats['total_original_sentences'] * 100) if sentence_stats['total_original_sentences'] > 0 else 0
        print(
            f"{'Total Sentences':<30} {sentence_stats['total_original_sentences']:>15,} {sentence_stats['total_cleaned_sentences']:>15,} {sent_change:>14.1f}%")

        # Word counts
        word_change = ((sentence_stats['total_cleaned_words'] - sentence_stats['total_original_words']) /
                       sentence_stats['total_original_words'] * 100) if sentence_stats['total_original_words'] > 0 else 0
        print(
            f"{'Total Words':<30} {sentence_stats['total_original_words']:>15,} {sentence_stats['total_cleaned_words']:>15,} {word_change:>14.1f}%")

        # Average sentence lengths
        char_change = ((sentence_stats['overall_clean_char_avg'] - sentence_stats['overall_orig_char_avg']) /
                       sentence_stats['overall_orig_char_avg'] * 100) if sentence_stats['overall_orig_char_avg'] > 0 else 0
        print(
            f"{'Avg Chars/Sentence':<30} {sentence_stats['overall_orig_char_avg']:>15.1f} {sentence_stats['overall_clean_char_avg']:>15.1f} {char_change:>14.1f}%")

        words_per_sent_change = ((sentence_stats['overall_clean_word_avg'] - sentence_stats['overall_orig_word_avg']) /
                                 sentence_stats['overall_orig_word_avg'] * 100) if sentence_stats['overall_orig_word_avg'] > 0 else 0
        print(
            f"{'Avg Words/Sentence':<30} {sentence_stats['overall_orig_word_avg']:>15.1f} {sentence_stats['overall_clean_word_avg']:>15.1f} {words_per_sent_change:>14.1f}%")

    def generate_detailed_report(self, file_stats: List[Dict], total_original: int, total_cleaned: int, show_chart: bool = True):
        """Generate detailed statistics report in console format."""
        # Only show console tables - no charts
        self._print_sentence_statistics_table(file_stats)
