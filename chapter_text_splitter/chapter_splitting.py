
from pathlib import Path
from utils import chinese_to_number, vietnamese_to_number

def get_text(file_path: Path) -> str:
    with open(file_path, 'r', encoding="utf-8") as f:
        texts = f.readlines()
    return texts

def chapter_splitting_file(file_path: Path, pattern: str):
    file_name = file_path.stem
    text = get_text(file_path)

def chapter_splitting_folder(input_folder: Path, pattern: str):
    txt_files = list(input_folder.glob("*.txt"))
    text_page_dict = {}
    for path in txt_files:
        chapter_splitting_file(path, pattern)

if __name__=="__main__":
    config_path = "./chapter_text_splitter/config_chapter_split.json"
    file_path = "./data/"