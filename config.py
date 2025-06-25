
import sys
import logging
from dataclasses import dataclass

@dataclass(frozen=True)
class GeneratorConfig:
    # 
    PAGE_BREAK: str = '\f\n'
    PARAGRAPH_BREAK: str = '\n\n'
    SENTENCE_BREAK: str = '\n'
    SINONOM_SECTION_TEMPLATE: str = r"^第([一二三四五六七八九十百千零〇○]+)[回囘]"
    QUOCNGU_SECTION_TEMPLATE: str = r"^HỒI THỨ ([\wÀ-Ỵ]+(?: [\wÀ-Ỵ]+)*)"

    # file and folder paths
    output_folder_path = './data'
    sinonom_pdf_path = './data/source/Book-Tay_Du_Ky-Trung.pdf'
    quocngu_pdf_path = './data/source/Book-Tay_Du_Ky-Viet.pdf'

    # extract sinonom text
    sinonom_start_page = 1      # first page = 1
    sinonom_num_pages = 542     # None = all
    
    # extract quocngu text
    quocngu_start_page = 48     # first page = 1
    quocngu_num_pages = 3368    # 3368 + 48 - 1 = 3415 (the last content page)

    # QuocNgu text normalization
    noise_json_path: str = './quocngu_normalizer/config_noise.json'     # None for not cleaning noise 

    # XML meta data
    xml_metadata = {
        "file id": "TDK_001",
        "title": "Tây Du Ký",
        "volume": "",
        "author": "Ngô Thừa Ân",
        "period": "Đại Minh",
        "language": "Hán-Việt",
        "translator": "Như Sơn, Mai Xuân Hải và Phương Oanh",
        "source": "gutenberg.org",
    }

    # Align options
    align_options = {
        "max_align": 6,         # limit the number of alignments (0-1, 1-0, ...) per sentence
        "top_k": 3,             # select the top-k candidate pairs
        "win": 6,               # sliding window.
        "skip": 0.0,            # skip sent pairs with sim score smaller than this.
        "margin": True,         # enable margin-based scoring.
        "len_penalty": True,    # penalize alignments with large difference in length.
        "is_split": True,       # condition check if paragraphs is slitted into sentences.
    }

    # Logging
    verbose: bool = True
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


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
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(GeneratorConfig.log_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, level.upper()))
        return logger
