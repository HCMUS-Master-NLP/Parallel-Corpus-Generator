
from typing import Literal, List, Dict
from pathlib import Path
import os
import re


def convert_list_to_dict(section: List) -> Dict:
    '''
    input: section = [[para_1_sent_1, ...], [para_2_sent_1, ...], ...]
    output: section_dict = {para_1_sent_1_id: para_1_sent_1, ...}
    '''
    section_dict = {}
    for i, para in enumerate(section):
        for j, sent in enumerate(para):
            id = f"{i:03}.{j+1:02}"
            section_dict[id] = sent
    return section_dict


def extract_sino_section_number(section):
    # Tìm dòng bắt đầu bằng "HỒI THỨ", sau đó lấy phần chữ phía sau
    match = re.search(r"^第([一二三四五六七八九十百千零〇○]+)[回囘]", section, re.MULTILINE)
    if match:
        return chinese_to_number(match.group(1).strip())
    return -1


def extract_quocngu_section_number(section):
    # Tìm dòng bắt đầu bằng "HỒI THỨ", sau đó lấy phần chữ phía sau
    match = re.search(r"^HỒI THỨ ([A-ZÀ-Ỵ\s\-]+)$", section, re.MULTILINE)
    if match:
        return vietnamese_to_number(match.group(1).strip())
    return -1

'''
sections = [section_text_1, section_text_2]
'''
def save_quocngu_sections(folder: Path, sections: List, verbose: bool = False) -> None:
    for section in sections:
        num = extract_quocngu_section_number(section)
        file_name = f"{num:03}"
        file_path = folder / f"{file_name}.txt"
        save_txt(section, file_path)
        if verbose:
            print(f"Successfully save file {file_path}")


def save_txt(text: str, file_path: str) -> None:
    file_path = Path(file_path)
    os.makedirs(file_path.parent, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


def vietnamese_to_number(vietnamese: str) -> int:
    viet_numerals = {
        'không': 0,
        'một': 1, 'mốt': 1, 'nhất': 1,
        'hai': 2, 'ba': 3, 'bốn': 4, 'tư': 4,
        'năm': 5, 'lăm': 5,
        'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9,
        'mười': 10
    }

    multipliers = {
        'mươi': 10,
        'trăm': 100,
        'nghìn': 1000,
        'triệu': 1000000,
        'tỷ': 1000000000
    }

    words = ' '.join(vietnamese.strip().split())
    words = words.lower()
    words = words.split(" ")

    number = 0
    current = 0
    i = 0
    while i < len(words):
        w = words[i]
        if w in viet_numerals.keys():
            current += viet_numerals[w]
        elif w in multipliers.keys():
            if current == 0:
                return -1
            number = number + current*multipliers[w]
            current = 0
        elif w in ["linh","lẻ"]:
            pass
        else:
            return -1
        i += 1

    if current != 0:
        number += current

    return number


# USE TO READ CHAPTER NUMBER IN TRANDITIONAL CHINESE TEXT
def chinese_to_number(hanzi) -> int:
    numerals = {
        '零': 0, '○': 0, '〇': 0,  # Thêm tất cả biến thể của số 0
        '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
        '十': 10
    }

    if hanzi == '十':
        return 10
    elif '十' in hanzi:
        parts = hanzi.split('十')
        left = numerals.get(parts[0], 1) if parts[0] else 1
        right = numerals.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
        return left * 10 + right
    else:
        total = 0
        for ch in hanzi:
            total = total * 10 + numerals[ch]
        return total