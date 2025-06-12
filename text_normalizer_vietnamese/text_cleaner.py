"""Main text cleaning functionality."""

import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from cleaning_config import CleaningConfig, LoggerMixin
from exceptions import TextCleanerError
from noise_pattern_manager import NoisePatternManager
from vietnamese_dictionary import VietnameseDictionary
from text_tokenizer import TextTokenizer
from punctuation_normalizer import PunctuationNormalizer


class TextCleaner(LoggerMixin):
    """Main class for cleaning Vietnamese OCR text with comprehensive processing pipeline."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        dictionary_path: Optional[Path] = None,
        config: Optional[CleaningConfig] = None,
        verbose: bool = False
    ):
        """Initialize the Vietnamese text cleaner."""
        log_level = 'INFO' if verbose else 'WARNING'
        super().__init__(logger_name=self.__class__.__name__, log_level=log_level)

        self.config = config or CleaningConfig()
        self.noise_manager = NoisePatternManager(config_path)
        self.dictionary = VietnameseDictionary(
            dictionary_path, self.config.case_sensitive_dictionary)
        self.tokenizer = TextTokenizer()
        self.punctuation_normalizer = PunctuationNormalizer(self.config)

        self._stats = defaultdict(int)
        self.logger.info("TextCleaner initialized successfully")

    def clean_text(self, text: str) -> str:
        """Execute the complete text cleaning pipeline."""
        try:
            self.logger.info("Starting comprehensive text cleaning pipeline")
            self._reset_stats()

            # Store original text for sentence statistics
            original_text = text

            # Pipeline stages
            text = self._apply_noise_removal(text)
            text = self._normalize_whitespace(text)
            tokens = self._tokenize_text(text)
            tokens = self._filter_valid_tokens(tokens)
            tokens = self._replace_underscores(tokens)
            cleaned_text = self._rejoin_and_normalize(tokens)
            text = self._filter_by_dictionary(text)

            # Calculate sentence statistics
            self._calculate_sentence_stats(original_text, cleaned_text)

            self._log_cleaning_stats()
            self.logger.info("Text cleaning pipeline completed successfully")

            return cleaned_text

        except Exception as e:
            self.logger.error("Text cleaning failed: %s", e)
            raise TextCleanerError(f"Cleaning process failed: {e}")

    def _calculate_sentence_stats(self, original_text: str, cleaned_text: str) -> None:
        """Calculate sentence count and average length statistics."""
        # Count sentences in original text
        original_sentences = self._count_sentences(original_text)
        self._stats['original_sentences'] = original_sentences

        # Count sentences in cleaned text
        cleaned_sentences = self._count_sentences(cleaned_text)
        self._stats['cleaned_sentences'] = cleaned_sentences

        # Count words in original and cleaned text
        original_words = len(original_text.split())
        cleaned_words = len(cleaned_text.split())

        # Store total word counts
        self._stats['original_words'] = original_words
        self._stats['cleaned_words'] = cleaned_words

        # Calculate average sentence length for original text
        if original_sentences > 0:
            original_avg_length = len(original_text) / original_sentences
            self._stats['original_average_sentence_length'] = round(
                original_avg_length, 1)

            # Calculate words per sentence for original text
            original_words_per_sentence = original_words / original_sentences
            self._stats['original_words_per_sentence'] = round(
                original_words_per_sentence, 1)
        else:
            self._stats['original_average_sentence_length'] = 0
            self._stats['original_words_per_sentence'] = 0

        # Calculate average sentence length for cleaned text
        if cleaned_sentences > 0:
            cleaned_avg_length = len(cleaned_text) / cleaned_sentences
            self._stats['cleaned_average_sentence_length'] = round(
                cleaned_avg_length, 1)

            # Calculate words per sentence for cleaned text
            cleaned_words_per_sentence = cleaned_words / cleaned_sentences
            self._stats['cleaned_words_per_sentence'] = round(
                cleaned_words_per_sentence, 1)
        else:
            self._stats['cleaned_average_sentence_length'] = 0
            self._stats['cleaned_words_per_sentence'] = 0

        self.logger.info("Sentence statistics calculated: %d -> %d sentences",
                         original_sentences, cleaned_sentences)

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text using Vietnamese sentence delimiters."""
        if not text.strip():
            return 0

        # Vietnamese sentence delimiters
        sentence_delimiters = r'[.!?;]+'

        # Split by sentence delimiters and count non-empty parts
        sentences = re.split(sentence_delimiters, text)
        # Filter out empty or whitespace-only sentences
        non_empty_sentences = [s for s in sentences if s.strip()]

        return len(non_empty_sentences)

    def _reset_stats(self) -> None:
        """Reset processing statistics."""
        self._stats.clear()

    def _apply_noise_removal(self, text: str) -> str:
        """Apply noise removal patterns."""
        if not self.noise_manager.patterns:
            return text

        original_length = len(text)
        cleaned_text = self.noise_manager.apply_patterns(text)

        self._stats['noise_chars_removed'] = original_length - \
            len(cleaned_text)
        self.logger.info("Applied %d noise patterns",
                         len(self.noise_manager.patterns))

        return cleaned_text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters."""
        return re.sub(r'\s+', ' ', text).strip()

    def _filter_by_dictionary(self, text: str) -> str:
        """Filter words based on Vietnamese dictionary."""
        if not self.dictionary.words:
            return text

        words = text.split()
        filtered_words = []

        for word in words:
            # Clean word for comparison (remove punctuation at start/end)
            clean_word = re.sub(
                rf'^[{self.config.PUNCTUATION}]+|[{self.config.PUNCTUATION}]+$', '', word)

            # Keep word if it's in dictionary, is punctuation only, or is empty after cleaning
            if (not clean_word or
                self.dictionary.contains(clean_word) or
                    self.config.punctuation_only_pattern.match(word)):
                filtered_words.append(word)
            else:
                self._stats['dictionary_words_removed'] += 1
                self.logger.debug("Removed word not in dictionary: %s", word)

        self.logger.info("Dictionary filter: removed %d words",
                         self._stats['dictionary_words_removed'])
        return ' '.join(filtered_words)

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text using configured tokenizer."""
        tokens = self.tokenizer.tokenize(text)
        self._stats['tokens_generated'] = len(tokens)
        self.logger.info("Generated %d tokens", len(tokens))
        return tokens

    def _filter_valid_tokens(self, tokens: List[str]) -> List[str]:
        """Filter tokens to keep only valid Vietnamese words and punctuation."""
        valid_tokens = []

        for token in tokens:
            if self._is_valid_token(token):
                valid_tokens.append(token)
            else:
                self._stats['invalid_tokens_removed'] += 1
                self.logger.debug("Filtered out invalid token: %s", token)

        self.logger.info("Kept %d valid tokens", len(valid_tokens))
        return valid_tokens

    def _is_valid_token(self, token: str) -> bool:
        """Check if token is valid based on configured patterns and length."""
        if not token:
            return False

        # Check length constraints
        if not (self.config.min_word_length <= len(token) <= self.config.max_word_length):
            return False

        # Check character patterns
        return (self.config.valid_token_pattern.match(token) or
                self.config.punctuation_only_pattern.match(token))

    def _replace_underscores(self, tokens: List[str]) -> List[str]:
        """Replace underscores with spaces in tokens."""
        processed_tokens = [token.replace('_', ' ') for token in tokens]
        self.logger.info("Replaced underscores with spaces")
        return processed_tokens

    def _rejoin_and_normalize(self, tokens: List[str]) -> str:
        """Rejoin tokens and apply final punctuation normalization."""
        rejoined_text = ' '.join(tokens)
        normalized_text = self.punctuation_normalizer.normalize(rejoined_text)
        return normalized_text

    def _log_cleaning_stats(self) -> None:
        """Log comprehensive cleaning statistics."""
        if self._stats:
            self.logger.info("Cleaning Statistics:")
            for key, value in self._stats.items():
                self.logger.info("  %s: %s", key, value)

    def get_cleaning_stats(self) -> Dict[str, int]:
        """Get current cleaning statistics."""
        return dict(self._stats)
