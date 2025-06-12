import logging
import os
import re
from typing import Literal

import numpy as np
import torch
from pypdf import PdfReader

from pathlib import Path
from transformers import pipeline

logger = logging.getLogger(__name__)

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# corrector = pipeline(
#     "text2text-generation", model="bmd1905/vietnamese-correction-v2", device=device
# )

import json

def load_removal_rules(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get("rules", [])

def remove_unwanted_lines(text: str, rules: list) -> str:
    lines = text.split("\n")
    result_lines = lines[:]

    for rule in rules:
        rule_type = rule["type"]

        if rule_type == "remove_above":
            keyword = rule["keyword"]
            for i, line in enumerate(result_lines):
                if keyword in line:
                    result_lines = result_lines[i:]  # giữ lại từ dòng chứa keyword trở xuống
                    break

        elif rule_type == "remove_below":
            keyword = rule["keyword"]
            for i, line in enumerate(result_lines):
                if keyword in line:
                    result_lines = result_lines[:i+1]  # giữ lại đến dòng chứa keyword
                    break

        elif rule_type == "contains":
            keywords = rule.get("keywords", [])
            result_lines = [
                line for line in result_lines
                if not any(keyword in line for keyword in keywords)
            ]

    return "\n".join(result_lines).strip()



# def is_poem_line(line: str) -> bool:
#     line = line.strip()
#     # Condition 1: Empty line → not poem
#     if not line:
#         return False

#     # Condition 2: Short line (less than 8 words) that starts with a capital
#     if len(line.split(" ")) <= 8 and re.match(
#         r"^[A-ZÁÀẢÃẠÂĂĐÊÉÈẺẼẸẾỀỂỄỆÔƠÓÒỎÕỌỐỒỔỖỘÚÙỦŨỤƯÝỲỶỸỴ]", line
#     ):
#         return True

#     return False


# def detect_blocks(text: str):
#     """
#     Separate the text into blocks:
#     - 'poem' for stanza-like short lines
#     - 'prose' for paragraph text
#     Returns: List of (type, lines) tuples
#     """
#     lines = text.splitlines()
#     blocks = []
#     current_block = []
#     current_type = None

#     for line in lines:
#         stripped = line.strip()
#         if not stripped:
#             # Blank line = block break
#             if current_block:
#                 blocks.append((current_type, current_block))
#                 current_block = []
#             current_type = None
#             continue

#         this_type = "poem" if is_poem_line(stripped) else "prose"

#         if current_type != this_type:
#             if current_block:
#                 blocks.append((current_type, current_block))
#                 current_block = []
#             current_type = this_type

#         current_block.append(stripped)

#     if current_block:
#         blocks.append((current_type, current_block))

#     return blocks


# def process_blocks(blocks):
#     """Rejoin prose blocks and keep poem blocks intact."""
#     result = []
#     for block_type, lines in blocks:
#         if block_type == "prose":
#             # Join lines unless punctuation ends the sentence
#             paragraph = ""
#             for line in lines:
#                 if paragraph and not re.search(r"[.?!:]$", paragraph):
#                     paragraph += " " + line
#                 else:
#                     if paragraph:
#                         result.append(paragraph)
#                     paragraph = line
#             if paragraph:
#                 result.append(paragraph)
#         else:
#             result.extend(lines)  # keep poem lines as-is
#         result.append("")  # paragraph break

#     return "\n".join(result).strip()


# def vietnamese_correction(texts: str) -> str:
#     """
#     Correct Vietnamese text using a pre-trained model.
#     """
#     MAX_LENGTH = 1024
#     # Batch prediction
#     predictions = corrector(
#         [text for text in texts.split("\n")], max_new_tokens=MAX_LENGTH
#     )
#     corrected_texts = [
#         corrected_text["generated_text"] for corrected_text in predictions
#     ]
#     return "\n".join(corrected_texts)


# def post_process_chinese(text: str, is_ocr=False) -> str:
#     """
#     Post-process Chinese text to remove footer note and header note.
#     """
#     # Remove unwanted characters
#     if is_ocr:
#         text = "\n".join(text.split("\n")[1:-2])
#     else:
#         text = "\n".join(text.split("\n")[:-2])
#     return text

# def post_process_chinese(text: str, is_ocr=False) -> str:
#     """
#     Clean Chinese text by removing unwanted headers/footers and filtering only Chinese paragraphs.
#     """
#     if not text:
#         return ""

#     lines = text.split("\n")

#     # Cắt bỏ dòng đầu/cuối theo kiểu OCR hoặc text thường
#     if is_ocr:
#         lines = lines[1:-2]  # bỏ dòng đầu và 2 dòng cuối
#     else:
#         lines = lines[:-2]   # bỏ 2 dòng cuối

#     # Ghép lại nội dung sau khi cắt dòng
#     clean_text = "\n".join(lines)

#     # Lọc ra các đoạn chứa chủ yếu là chữ Hán hoặc dấu câu tiếng Trung
#     chinese_blocks = re.findall(
#         r'[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef。，、“”《》！？：；（）\s]{5,}', 
#         clean_text
#     )

#     return '\n'.join(block.strip() for block in chinese_blocks if block.strip())

def post_process_chinese(text: str, removal_rules, use_rules=False, is_ocr=False) -> str:
    if not text:
        return ""
    lines = text.split("\n")

    # Bỏ dòng đầu/cuối
    lines = lines[1:-2] if is_ocr else lines[:-2]
    clean_text = "\n".join(lines)

    # Áp dụng loại bỏ theo rules
    if use_rules:
        clean_text = remove_unwanted_lines(clean_text, removal_rules)

    # Chỉ giữ lại đoạn chứa nhiều chữ Hán
    chinese_blocks = re.findall(
        r'[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef。，、“”《》！？：；（）\s]{5,}',
        clean_text
    )

    return "\n".join(block.strip() for block in chinese_blocks if block.strip())
    # return clean_text


def post_process_vietnamese(text: str, removal_rules, use_rules=False, is_ocr=False) -> str:
    if not text:
        return ""
    # Áp dụng loại bỏ theo rules
    if use_rules:
        clean_text = remove_unwanted_lines(text, removal_rules)

    return clean_text


# def clean_ocr_text(text: str, lang: str) -> str:
#     """
#     Clean and process OCR text based on language.
#     """
#     if lang == "chi_tra":
#         cleaned = text.replace("\n\n", "\n")
#         cleaned = post_process_chinese(cleaned)

#     if lang == "vie":
#         blocks = detect_blocks(text)
#         cleaned = process_blocks(blocks)
#         cleaned = vietnamese_correction(cleaned)
#         cleaned_blocks = detect_blocks(cleaned)
#         cleaned = process_blocks(cleaned_blocks)
#         cleaned = cleaned.replace("\n\n", "\n")
#     return cleaned


# def save_text_in_page(text, output_file):
#     """
#     Save the extracted text to a file.

#     text: Text to be saved.
#     output_file: Path to the output file.
#     """
#     with open(output_file, "a+", encoding="utf-8") as f:
#         f.write(text)
#         f.write("\n")  # Add a newline for separation between pages
#     logger.info(f"Text saved to {output_file}")


def save_text(text: str, output_file: str, page_number: int = None):
    """
    Save the extracted text to a file.

    Args:
        text: Text to be saved.
        output_file: Path to the output file.
        page_number: (Optional) Page number to label the section.
    """
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(output_file.parent, exist_ok=True)

    with open(output_file, "a+", encoding="utf-8") as f:
        f.write(text.strip())

    logger.info(f"✅ Page {page_number if page_number else '[unknown]'} saved to {output_file}")


def get_pdf_name(file_name):
    """
    Extract the base name of the PDF file without extension.

    file_name: Full path to the PDF file.
    return: Base name of the PDF file.
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"The file {file_name} does not exist.")

    # Extract the base name without extension
    pdf_name = file_name.split("/")[-1].split(".")[0]
    return pdf_name


def read_pdf(pdf_path, first_page, last_page, rule_path, use_rules, lang: Literal["vie", "chi_tra"] = "vie"):
    """
    Read pdf
    """
    removal_rules = load_removal_rules(rule_path)
    reader = PdfReader(pdf_path)
    texts = []
    for i, page in enumerate(reader.pages[first_page-1:last_page]):
        page_content = page.extract_text()
        if lang=="chi_tra":
            page_content = post_process_chinese(page_content, removal_rules, use_rules)
        else:
            page_content = post_process_vietnamese(page_content, removal_rules, use_rules)
        texts.append(page_content)

    return texts


def normalize_paragraphs(lines):
    paragraph = ""
    paragraphs = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        paragraph += line
        # Nếu câu kết thúc
        if re.search(r'[。！？；…」]$', line):
            paragraphs.append(paragraph)
            paragraph = ""
    if paragraph:  # còn sót
        paragraphs.append(paragraph)
    return paragraphs


def extract_pdf_to_text(
    pdf_path: Path,
    output_dir: Path,
    first_page,
    num_pages,
    rule_path: Path,
    use_rules: bool,
    lang: Literal["vie", "chi_tra"] = "vie",
    use_page_split: bool = False
):
    """
    Read pdf and save to txt file
    """
    last_page = first_page + num_pages - 1

    pages_content = read_pdf(pdf_path, first_page, last_page, rule_path, use_rules, lang)

    # Lưu văn bản
    if use_page_split:
        for i, content in enumerate(pages_content):
            page_num = first_page + i
            output_file = output_dir.joinpath(f"{page_num:03d}.txt")

            if output_file.is_file():
                os.remove(output_file)
            content = normalize_paragraphs(content)
            save_text(content, output_file, page_num)
    else:
        output_file = output_dir.joinpath(f"{pdf_path.stem}.txt")
        save_text("\n".join(pages_content), output_file)
