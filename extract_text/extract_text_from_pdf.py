import fitz     # pymupdf
from pathlib import Path
import os
from typing import Optional, Literal
from process_extracted_text import cleanup_extracted_chinese
from config import PAGE_BREAK, PARAGRAPH_BREAK, SENTENCE_BREAK
def extract_text_simple(
    file_path: str,
    start_page: int = 1,
    num_pages: Optional[int] = None
) -> str:
    file_path = Path(file_path)
    
    with fitz.open(file_path) as pdf_file:
        # convert 1-based to 0-based index
        start_idx = max(start_page - 1, 0)
        
        if num_pages is not None:
            end_idx = min(start_idx + num_pages, len(pdf_file))
        else:
            end_idx = len(pdf_file)
        
        text = "".join([
            pdf_file[i].get_text("text") + PAGE_BREAK
            for i in range(start_idx, end_idx)
        ])
    
    return text


def extract_text_preserve_paragraph(
    file_path: str, 
    start_page: int = 1, 
    num_pages: Optional[int] = None
) -> str:
    file_path = Path(file_path)
    
    with fitz.open(file_path) as pdf:
        start_idx = max(start_page - 1, 0)
        end_idx = min(len(pdf), start_idx + num_pages) if num_pages else len(pdf)
        pages_text = []
        for i in range(start_idx, end_idx):
            blocks = pdf[i].get_text("dict")["blocks"]
            paragraphs = [] # set of paragraphs in a page
            for block in blocks:    # each block is roughly equal to a paragraph 
                if "lines" not in block:
                    continue
                lines = []  # set of lines in a parapragh
                for line in block["lines"]:
                    span_texts = []
                    for span in line["spans"]:
                        span_texts.append(span["text"])
                    lines.append(" ".join(span_texts))
                
                # add "\n" at the end of each line in a paragraph
                paragraphs.append("".join([line + SENTENCE_BREAK for line in lines]))

            # add "\n\n" at the end of each paragraph in a page
            pages_text.append("".join([p + PARAGRAPH_BREAK for p in paragraphs]))

        # add "chr(12)\n" or "\f\n" at the end of each page in pdf document
        pages_text = "".join([text + PAGE_BREAK for text in pages_text])
        
    return pages_text


def extract_text_from_pdf(
    file_path: str, 
    start_page: int = 1, 
    num_pages: Optional[int] = None,    # None if extract from start page to the end page
    lang: Literal["vie","chi_tra"] = "chi_tra"
) -> str:
    if lang=="chi_tra":
        text = extract_text_preserve_paragraph(file_path,start_page,num_pages)
        text = cleanup_extracted_chinese(text)
        return text
    else:
        return extract_text_simple(file_path,start_page,num_pages)


def save_text(text: str, file_path: str) -> None:
    file_path = Path(file_path)
    os.makedirs(file_path.parent, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


if __name__=="__main__":
    lang = "chi_tra"    
    input_path = ""  
    output_path = ""
    text = ""
    if lang == "vie":
        input_path = "D:/tmp/Parallel-Corpus-Generator/data/source/Book-Tay_Du_Ky-Viet.pdf"
        output_path = "D:/tmp/Parallel-Corpus-Generator/data/raw/vietnamese/Book-Tay_Du_Ky-Viet.txt"
        text = extract_text_from_pdf(input_path,48,3,lang)
    else:
        input_path = "D:/tmp/Parallel-Corpus-Generator/data/source/Book-Tay_Du_Ky-Trung.pdf"
        output_path = "D:/tmp/Parallel-Corpus-Generator/data/raw/chinese_traditional/Book-Tay_Du_Ky-Trung.txt"
        text = extract_text_from_pdf(input_path,1,None,lang)
    
    save_text(text, output_path)