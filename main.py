
from pdf_extractor import SinoNomPDFExtractor, QuocNguPDFExtractor
from sinonom_preprocessing import sinonom_preprocessing, split_chinese_sentences, normalize_chinese_text
from pathlib import Path
import os
from typing import Literal

CHINESE_CHAPTER_TEMPLATE = r"^第[一二三四五六七八九十百千零〇○]+[回囘]"
VIETNAMESE_CHAPTER_TEMPLATE = r"^HỒI THỨ(?: [\wÀ-Ỵ]+)+$"

if __name__=="__main__":
    lang = "vie"    
    input_path = ""  
    output_path = ""
    text = ""

    QN_input_path = "./data/source/Book-Tay_Du_Ky-Viet.pdf"
    SN_input_path = "./data/source/Book-Tay_Du_Ky-Trung.pdf"

    QN_output_path = "./data/raw/vietnamese/Book-Tay_Du_Ky-Viet.txt"
    SN_output_path = "./data/raw/chinese_traditional/Book-Tay_Du_Ky-Trung.txt"
    
    # sino_extractor = SinoNomPDFExtractor(SN_input_path, 1, 10)
    quocngu_extractor = QuocNguPDFExtractor(QN_input_path, 48, 50)

    # SN_sections = sino_extractor.get_splitted_sections(CHINESE_CHAPTER_TEMPLATE)
    QN_sections = quocngu_extractor.get_splitted_sections(VIETNAMESE_CHAPTER_TEMPLATE)



    # for s in SN_sections:
    #     print(s)

    # for s in SN_sections:
    #     text = sinonom_preprocessing(s)
    #     print(text)

    # text = "詩曰: 混沌未分天地亂，茫茫渺渺無人見。自從盤古破鴻濛，開闢從茲清濁辨。"
    # text = normalize_chinese_text(text)
    # text = split_chinese_sentences(text)
    # print(text)
