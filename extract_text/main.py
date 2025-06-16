import argparse
import logging
import sys
from pathlib import Path

# from text_img_utils import (
#     extract_pdf_to_text,
#     # get_pdf_name
# )

from extract_text_from_pdf import extract_text_from_pdf


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR PDF files.")
    parser.add_argument("-l","--lang",type=str,default="viet",choices=["viet", "trung"],help="Language for OCR (default: 'vie' for Vietnamese)")
    parser.add_argument("-p", "--pdf_path",type=str,required=True,help="Path to the PDF file to be processed.")
    parser.add_argument("-fp", "--first_page",type=int,default=0,help="First page to start OCR (default: 0)")
    parser.add_argument("-np", "--num_pages",type=int,default=20,help="Number of pages to process (default: 20)")
    parser.add_argument("-pt", "--process_text",type=bool,default=True,help="Apply processing to the OCR text (default: True)")
    parser.add_argument("-o", "--output_dir",type=str,default=".",help="Path to save PDF text.")
    return parser

def main():
    logger = logging.getLogger(__name__)
    parser = create_argument_parser()
    args = parser.parse_args()
    
    data = {
        "viet": {
            "pdf_path": ".\Book-Tay_Du_Ky-Viet.pdf",
            "lang": "vie",
            "output_dir": ".",
        },
        "trung": {
            "pdf_path": ".\Book-Tay_Du_Ky-Trung.pdf",
            "lang": "chi_tra",
            "output_dir": ".",
        },
    }

    if args.lang is None:
        lang = "viet"
    else:
        lang = args.lang
        
    if args.output_dir != ".":
        data[lang]["output_dir"] = args.output_dir
        
    if args.pdf_path is None:
        pdf_path = '.\Book-Tay_Du_Ky-Viet.pdf'
    else:
        data[lang]["pdf_path"] = args.pdf_path
        
    pdf_path = Path(data[lang]["pdf_path"])
    pdf_name = pdf_path.stem
    pdf_lang = data[lang]["lang"]
    output_dir = Path(data[lang]["output_dir"])
    rule_path = Path(args.rule_path)

    # Validate input pdf file
    if not pdf_path.exists():
        print(
            f"Error: PDF path '{pdf_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    logger.info(f"Processing {pdf_name} in {pdf_lang} language at {pdf_path}...")
    extract_text_from_pdf(
        pdf_path, 
        output_dir=output_dir, 
        first_page=args.first_page, 
        num_pages=args.num_pages, 
        lang=pdf_lang)
    logger.info(f"Finished processing {pdf_name} in {pdf_lang} language.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    main()