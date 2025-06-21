
from pathlib import Path
from typing import Literal, Optional
import os
import fitz  # PyMuPDF
# from pypdf import PdfReader


def save_text_to_txt(
    text: str,
    output_path: Path,
    verbose: bool = False
) -> None:
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(output_path.parent, exist_ok=True)

    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(text)
    
    if verbose:
        print(f"Text is saved to {output_path}!!!")


def extract_preserve_paragraph_space(
    pdf_path: Path, 
    lang: Literal['vie', 'lzh'] = 'vie',
    first_page: int = 1, 
    num_pages: Optional[int] = None,
    verbose: bool = False,
    header_threshold_ratio: float = 0.03,   # remove line in header
    footer_threshold_ratio: float = 0.95    # remove line in footer
) -> str:
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    start = max(first_page - 1, 0)
    end = start + num_pages if num_pages is not None else total_pages

    full_text = ""

    for i in range(start, min(end, total_pages)):
        page = doc[i]
        page_height = page.rect.height
        blocks = page.get_text("blocks")
        sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort by y0, x0

        for block in sorted_blocks:
            y0, y1 = block[1], block[3]
            text = block[4].strip()

            # remove blocks if they are in header or footer area
            if y0 < page_height * header_threshold_ratio:
                continue
            if y1 > page_height * footer_threshold_ratio:
                continue

            if text:
                full_text += text + "\n\n"

    if verbose:
        print(f"Extracted text from {str(pdf_path)} successfully!")

    return full_text.strip()

# lang: Literal['vie', 'lzh'] = 'vie',
# verbose: bool = False,
# header_threshold_ratio: float = 0.03,   # remove line in header
# footer_threshold_ratio: float = 0.95    # remove line in footer
# def extract_text_from_pdf(
#     pdf_path: Path, 
#     first_page: int = 1, 
#     num_pages: Optional[int] = None, 
# ) -> str:

#     pdf_file = fitz.open(str(pdf_path))

#     text = ""
#     # STEP 3
#     # iterate over PDF pages
#     for page_index in range(len(pdf_file)):

#         # get the page itself
#         page = pdf_file.load_page(page_index)  # load the page
        
#         page_text = page.get_text() + chr(12)
#         print('\t' + page_text)
        
#         dictionary_elements = page.get_text('dict')
#         for block in dictionary_elements['blocks']:
#             line_text = ''
#             for line in block['lines']:
#                 for span in line['spans']:
#                     line_text += ' ' + span['text']
#                 # print('\t' + line_text)

def extract_text_from_pdf(
    pdf_path: Path, 
    first_page: int = 1, 
    num_pages: Optional[int] = None, 
) -> str:
    pdf_file = fitz.open(str(pdf_path))
    total_pages = len(pdf_file)

    # Điều chỉnh trang bắt đầu (fitz sử dụng index từ 0)
    start = max(0, first_page - 1)
    
    # Xác định số lượng trang cần đọc
    if num_pages is not None:
        end = min(start + num_pages, total_pages)
    else:
        end = total_pages

    text = ""

    # Lặp qua các trang cần thiết
    for page_index in range(start, end):
        page = pdf_file.load_page(page_index)  # load trang
        page_text = page.get_text() + chr(12)  # chr(12) = form feed
        text += page_text

        print(f"\nTrang {page_index + 1}:")
        print('\t' + page_text.replace('\n', '\n\t'))

        # In dạng dictionary để xem cấu trúc chi tiết
        dictionary_elements = page.get_text('dict')
        for block in dictionary_elements['blocks']:
            line_text = ''
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        line_text += ' ' + span['text']
                # print('\t[Dòng trích xuất]:', line_text.strip())

    pdf_file.close()
    return text


if __name__=="__main__":
    # pdf_path = Path('D:/00_Temp files/Parallel-Corpus-Generator/data/source/Book-Tay_Du_Ky-Trung.pdf')
    # output_path = Path('D:/00_Temp files/Parallel-Corpus-Generator/data/raw_text/Book-Tay_Du_Ky-Trung.txt')
    # text = extract_text_from_pdf(pdf_path, 'lzh', 1, 5, True)
    
    pdf_path = Path('D:/00_Temp files/Parallel-Corpus-Generator/data/source/Book-Tay_Du_Ky-Viet.pdf')
    output_path = Path('D:/00_Temp files/Parallel-Corpus-Generator/data/raw_text/Book-Tay_Du_Ky-Viet.txt')
    # text = extract_text_from_pdf(pdf_path, 'lzh', 48, 5, True)
    text = extract_text_from_pdf(pdf_path, 48, 2)

    save_text_to_txt(text, output_path)