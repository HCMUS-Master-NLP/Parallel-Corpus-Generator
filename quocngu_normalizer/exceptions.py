"""Custom exceptions for text cleaning."""


class TextCleanerError(Exception):
    """Base exception for TextCleaner operations."""


class ConfigurationError(TextCleanerError):
    """Raised when configuration loading fails."""


class DictionaryError(TextCleanerError):
    """Raised when dictionary operations fail."""


class FileProcessingError(TextCleanerError):
    """Raised when file processing fails."""
