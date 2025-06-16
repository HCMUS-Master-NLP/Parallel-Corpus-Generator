
from pathlib import Path
from utils import chinese_to_number, vietnamese_to_number


# USE TO GET CHAPTER NUMBER IN VIETNAMESE TEXT
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
    


if __name__=="__main__":
    hanzi = "七二"
    number = chinese_to_number(hanzi)
    print(f"{hanzi}: {number}")
    
    viet = "HAI MƯƠI LĂM"
    number = vietnamese_to_number(viet)
    print(f"{viet}: {number}")