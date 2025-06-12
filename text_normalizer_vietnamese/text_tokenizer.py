"""Text tokenization with fallback mechanisms."""

import logging
from typing import List

# Optional dependency for advanced tokenization
try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False


class TextTokenizer:
    """Handles text tokenization with fallback mechanisms."""

    def __init__(self):
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")
        self.has_advanced_tokenizer = HAS_UNDERTHESEA

        if self.has_advanced_tokenizer:
            self.logger.info("Using advanced tokenization (underthesea)")
        else:
            self.logger.info("Using simple whitespace tokenization")

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using best available method."""
        if self.has_advanced_tokenizer:
            try:
                return word_tokenize(text, format='text').split()
            except Exception as e:
                self.logger.warning(
                    "Advanced tokenization failed, falling back to simple: %s", e)

        return self._simple_tokenize(text)

    @staticmethod
    def _simple_tokenize(text: str) -> List[str]:
        """Simple whitespace-based tokenization fallback."""
        return text.split()
