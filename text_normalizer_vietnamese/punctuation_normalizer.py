"""Punctuation normalization according to Vietnamese standards."""

import logging
import re

from cleaning_config import CleaningConfig


class PunctuationNormalizer:
    """Handles punctuation normalization according to Vietnamese standards."""

    def __init__(self, config: CleaningConfig):
        self.config = config
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def normalize(self, text: str) -> str:
        """Normalize punctuation spacing according to Vietnamese standards."""
        text = self._normalize_standard_punctuation(text)
        text = self._normalize_brackets_and_quotes(text)
        text = self._clean_whitespace(text)
        return text

    def _normalize_standard_punctuation(self, text: str) -> str:
        """Normalize spacing around standard punctuation marks."""
        punctuation_marks = ['.', ',', '!', '?', ':', ';', '…']

        for punct in punctuation_marks:
            # Remove spaces before punctuation
            text = re.sub(rf'\s+{re.escape(punct)}', punct, text)
            # Add space after punctuation if followed by word characters
            text = re.sub(
                rf'(?<={re.escape(punct)})(?=[^\s.,!?:;…])',
                ' ',
                text
            )

        return text

    def _normalize_brackets_and_quotes(self, text: str) -> str:
        """Normalize spacing around brackets and quotes."""
        # Brackets
        # Remove space after opening
        text = re.sub(r'([\(\[\{])\s+', r'\1', text)
        text = re.sub(r'\s+([\)\]\}])', r'\1',
                      text)  # Remove space before closing
        text = re.sub(r'([\)\]\}])(?=[^\s.,!?:;…\)\]\}])',
                      r'\1 ', text)  # Space after closing

        # Quotes
        # Remove space after opening
        text = re.sub(r'([""''])\s+', r'\1', text)
        # Remove space before closing
        text = re.sub(r'\s+([""''])', r'\1', text)
        text = re.sub(r'(?<=\w)([""''])', r' \1', text)  # Space before opening
        text = re.sub(r'([""''])(?=\w)', r'\1 ', text)  # Space after closing

        return text

    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """Clean up multiple spaces and trim."""
        return re.sub(r'\s+', ' ', text).strip()
