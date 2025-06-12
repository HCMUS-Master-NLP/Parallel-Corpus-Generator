"""Configuration and logging for text cleaning."""

import logging
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CleaningConfig:
    """Configuration settings for text cleaning operations."""

    # Character patterns
    VIETNAMESE_CHARS: str = r'\w\u00C0-\u017F\u1EA0-\u1EF9'
    PUNCTUATION: str = r'.,!?:;""''()""''…–—\\-'

    # Processing options
    min_word_length: int = 1
    max_word_length: int = 50
    preserve_punctuation: bool = True
    case_sensitive_dictionary: bool = False

    # Logging
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @property
    def valid_token_pattern(self) -> re.Pattern:
        """Compiled regex pattern for valid tokens."""
        return re.compile(rf'^[{self.VIETNAMESE_CHARS}{self.PUNCTUATION}]+$', re.UNICODE)

    @property
    def punctuation_only_pattern(self) -> re.Pattern:
        """Compiled regex pattern for punctuation-only tokens."""
        return re.compile(rf'^[{self.PUNCTUATION}]+$', re.UNICODE)


class LoggerMixin:
    """Mixin to provide consistent logging capabilities."""

    def __init__(self, logger_name: str = None, log_level: str = 'INFO'):
        self.logger = self._setup_logger(
            logger_name or self.__class__.__name__, log_level)

    @staticmethod
    def _setup_logger(name: str, level: str) -> logging.Logger:
        """Setup and configure logger."""
        logger = logging.getLogger(name)
        if not logger.handlers:  # Avoid duplicate handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter(CleaningConfig.log_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper()))
        return logger
