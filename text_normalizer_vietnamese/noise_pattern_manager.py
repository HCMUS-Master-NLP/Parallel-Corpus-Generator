"""Noise pattern management for text cleaning."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from exceptions import ConfigurationError


class NoisePatternManager:
    """Manages noise patterns for text cleaning."""

    def __init__(self, config_path: Optional[Path] = None):
        self.patterns: List[Dict[str, str]] = []
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

        if config_path:
            self.load_patterns(config_path)

    def load_patterns(self, config_path: Path) -> None:
        """Load noise patterns from configuration file."""
        if not config_path.exists():
            self.logger.warning(
                "Pattern config file not found: %s", config_path)
            return

        try:
            with config_path.open('r', encoding='utf-8') as f:
                raw_patterns = json.load(f)

            self.patterns = self._validate_and_normalize_patterns(raw_patterns)
            self.logger.info("Loaded %d noise patterns", len(self.patterns))

        except (json.JSONDecodeError, IOError) as e:
            raise ConfigurationError(
                f"Failed to load patterns from {config_path}: {e}")

    def _validate_and_normalize_patterns(self, raw_patterns: Union[List[Dict], List[str]]) -> List[Dict[str, str]]:
        """Validate and normalize pattern format."""
        if not raw_patterns:
            return []

        validated_patterns = []

        for item in raw_patterns:
            if isinstance(item, dict) and 'pattern' in item:
                # New format: {"pattern": "...", "replacement": "..."}
                validated_patterns.append({
                    'pattern': item['pattern'],
                    'replacement': item.get('replacement', '')
                })
            elif isinstance(item, str):
                # Legacy format: just pattern strings
                validated_patterns.append({
                    'pattern': item,
                    'replacement': ''
                })
            else:
                self.logger.warning("Invalid pattern format: %s", item)

        return validated_patterns

    def apply_patterns(self, text: str) -> str:
        """Apply all loaded patterns to text."""
        if not self.patterns:
            return text

        for pattern_dict in self.patterns:
            try:
                pattern = pattern_dict['pattern']
                replacement = pattern_dict['replacement']
                text = re.sub(pattern, replacement, text)
            except re.error as e:
                self.logger.warning(
                    "Invalid regex pattern '%s': %s", pattern, e)
                continue

        return text
