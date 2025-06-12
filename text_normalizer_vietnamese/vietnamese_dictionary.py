"""Vietnamese dictionary management for word validation."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from exceptions import DictionaryError


class VietnameseDictionary:
    """Manages Vietnamese dictionary for word validation."""

    def __init__(self, dict_path: Optional[Path] = None, case_sensitive: bool = False):
        self.words: Set[str] = set()
        self.case_sensitive = case_sensitive
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

        if dict_path:
            self.load_dictionary(dict_path)

    def load_dictionary(self, dict_path: Path) -> None:
        """Load Vietnamese dictionary from JSON file."""
        if not dict_path.exists():
            self.logger.warning("Dictionary file not found: %s", dict_path)
            return

        try:
            with dict_path.open('r', encoding='utf-8') as f:
                dictionary_data = json.load(f)

            self.words = self._extract_words(dictionary_data)
            self.logger.info(
                "Loaded %d Vietnamese words from dictionary", len(self.words))

        except (json.JSONDecodeError, IOError) as e:
            raise DictionaryError(
                f"Failed to load dictionary from {dict_path}: {e}")

    def _extract_words(self, dictionary_data: List[Dict]) -> Set[str]:
        """Extract Vietnamese words from dictionary data."""
        words = set()

        for entry in dictionary_data:
            if isinstance(entry, dict) and 'QuocNgu' in entry:
                word = entry['QuocNgu'].strip()
                if word:  # Only add non-empty words
                    words.add(word if self.case_sensitive else word.lower())

        return words

    def contains(self, word: str) -> bool:
        """Check if word exists in dictionary."""
        if not self.words:
            return True  # If no dictionary loaded, accept all words

        check_word = word if self.case_sensitive else word.lower()
        return check_word in self.words

    def filter_words(self, words: List[str]) -> Tuple[List[str], int]:
        """Filter words based on dictionary, return filtered words and removal count."""
        if not self.words:
            return words, 0

        filtered_words = []
        removed_count = 0

        for word in words:
            if self.contains(word):
                filtered_words.append(word)
            else:
                removed_count += 1

        return filtered_words, removed_count
