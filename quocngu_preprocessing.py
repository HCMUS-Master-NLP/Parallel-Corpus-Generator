import re
from pathlib import Path
from typing import List
from quocngu_normalizer.text_cleaner import TextCleaner

class QuocNguPreprocessor:
    def __init__(self, config_path=None):
        self.cleaner = TextCleaner(config_path=config_path)
    
    def normalize(self, text: str) -> str:
        norm_text = self.cleaner.clean_text(text)
        return norm_text
    
    def split_sents(self, text: str) -> List:
        """
        Split a Vietnamese text into sentences.
        Uses regex to identify sentence boundaries based on punctuation marks.
        """
        if not text.strip():
            return []

        # Remove extra whitespace and normalize the text
        text = re.sub(r'\s+', ' ', text.strip())

        # Define sentence ending patterns for Vietnamese text
        sentence_endings = r'[.!?…]+'

        # Split by sentence endings and keep the punctuation
        parts = re.split(f'({sentence_endings})', text)

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

    def norm_and_split(self, text: str) -> List:
        norm_text = self.normalize(text)
        return self.split_sents(norm_text)

def split_quocngu_sentences(text: str) -> List:
    """
    Split a Vietnamese text into sentences.
    Uses regex to identify sentence boundaries based on punctuation marks.
    """
    if not text.strip():
        return []

    # Remove extra whitespace and normalize the text
    text = re.sub(r'\s+', ' ', text.strip())

    # Define sentence ending patterns for Vietnamese text
    sentence_endings = r'[.!?…]+'

    # Split by sentence endings and keep the punctuation
    parts = re.split(f'({sentence_endings})', text)

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

def quocngu_preprocessing(text: str) -> List:
    cleaner = TextCleaner(config_path=Path("./quocngu_normalizer/config_noise.json"))
    if cleaner.noise_manager.patterns:
        text = cleaner.clean_text(text)
        text = split_quocngu_sentences(text)
    return text