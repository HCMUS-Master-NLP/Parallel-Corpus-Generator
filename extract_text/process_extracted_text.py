import re
from config import PARAGRAPH_BREAK, PAGE_BREAK, SENTENCE_BREAK

def is_traditional_chinese_line(line: str, threshold: float = 0.9) -> bool:
    # Loại bỏ khoảng trắng
    line = line.strip()
    if not line:
        return False

    # Đếm tổng số ký tự đáng kể
    total_chars = len([c for c in line if not c.isspace()])
    if total_chars == 0:
        return False

    # Regex ký tự Hán + dấu câu truyền thống
    # han_char_pattern = re.compile(r'[\u4e00-\u9fff○，。！？、：「」『』《》…；（）〔〕—]+')
    han_char_pattern = re.compile(r'['
        r'\u3400-\u4DBF'     # CJK Extension A
        r'\u4E00-\u9FFF'     # CJK Unified Ideographs
        r'\uF900-\uFAFF'     # Compatibility Ideographs
        r'\u2E80-\u2EFF'     # CJK Radicals Supplement
        r'\u2F00-\u2FDF'     # Kangxi Radicals
        r'\u2FF0-\u2FFF'     # Ideographic Description
        r'\u3007'            # 〇 (zero)
        r'\u25CB'            # ○ (circle)
        r'〇○零'             # Hán số 0, hình tròn, "linh"
        r'，。！？、：「」『』《》…；（）〔〕—“”'
        r']+')
    han_chars = ''.join(han_char_pattern.findall(line))

    # Tính tỉ lệ Hán văn
    ratio = len(han_chars) / total_chars

    return ratio >= threshold


def is_cjk_unified_char(ch: str) -> bool:
    return 0x4E00 <= ord(ch) <= 0x9FFF


def is_likely_continuation(prev_paragraph: str, curr_paragraph: str) -> bool:
    '''check if two paragraphs might be from one paragraph'''
    prev_last_line = [s for s in prev_paragraph.split(SENTENCE_BREAK) if s.strip()][-1]
    curr_first_line = [s for s in curr_paragraph.split(SENTENCE_BREAK) if s.strip()][0]
    
    # Must be the first condition
    if bool(re.search(r"第[一二三四五六七八九十百千萬〇○零]+回", prev_last_line)):
        return False
    
    # if the last character is Han char means paragraph is splitted
    if is_cjk_unified_char(prev_last_line[-1]):
        return True
    
    # same with last Hanzi character
    if prev_last_line[-1] in ["：","、","，"]:
        return True
    
    # if a paragraph is not done cause missing closing parenthesis
    if (prev_paragraph.count("」") < prev_paragraph.count("「")) or (prev_paragraph.count("』") < prev_paragraph.count("『")):
        return True
    
    # if first line of paragraph is have long white spaces, it can be the line of poetry
    if (len(curr_first_line) - len(curr_first_line.lstrip()) >= 2):
        return True
    
    return False


def merge_splitted(text: str) -> str:
    '''Merge any two adjacent paragraphs in text if they are from one paragraph'''
    pages = [p for p in text.split(PAGE_BREAK) if p.strip()]
    if not pages:
        return text
    
    # merge paragraphs within a page
    repaired_pages = []
    for page in pages:
        # Split by using SENTENCE_BREAK AND PARAGRAPH_BREAK because we just want to get raw text with no SENTENCE BREAK at the end of each paragraph
        paragraphs = [p for p in page.split(SENTENCE_BREAK+PARAGRAPH_BREAK) if p.strip()]
        repaired_paragraphs = [paragraphs[0]]
        for i in range(1,len(paragraphs)):
            if is_likely_continuation(repaired_paragraphs[-1], paragraphs[i]):
                repaired_paragraphs[-1] = repaired_paragraphs[-1] + paragraphs[i]
            else:
                repaired_paragraphs.append(paragraphs[i])        
        repaired_pages.append("".join(p + SENTENCE_BREAK + PARAGRAPH_BREAK for p in repaired_paragraphs))
    pages = repaired_pages
    
    # merge paragraphs across pages
    repaired_pages = [pages[0]]
    for i in range(1,len(pages)):
        # Split by using SENTENCE_BREAK AND PARAGRAPH_BREAK because we just want to get raw text with no SENTENCE BREAK at the end of each paragraph
        prev_paragraphs = [p for p in repaired_pages[-1].split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]
        curr_paragraphs = [p for p in pages[i].split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]
        
        if prev_paragraphs and curr_paragraphs:
            if is_likely_continuation(prev_paragraphs[-1], curr_paragraphs[0]):
                prev_paragraphs[-1] = prev_paragraphs[-1] + curr_paragraphs[0]
                curr_paragraphs = curr_paragraphs[1:]
        
        prev_page = "".join(p + SENTENCE_BREAK + PARAGRAPH_BREAK for p in prev_paragraphs)
        curr_page = "".join(p + SENTENCE_BREAK + PARAGRAPH_BREAK for p in curr_paragraphs)
        
        repaired_pages[-1] = prev_page
        if curr_page.strip():  # add only if curr_page has content
            repaired_pages.append(curr_page)
    
    repaired_pages = "".join(p + PAGE_BREAK for p in repaired_pages)
    return repaired_pages


def remove_endline(text: str) -> str:
    '''Remove every sentence break at the end of each line'''
    text = [p for p in text.split(PAGE_BREAK) if p.strip()]
    processed_text = []
    for page_text in text:
        page_text = [p for p in page_text.split(SENTENCE_BREAK+PARAGRAPH_BREAK) if p.strip()]
        
        # remove endline in each paragraph of a page
        processed_page_text = [paragraph.replace(SENTENCE_BREAK," ") for paragraph in page_text]
        
        processed_text.append("".join([p + PARAGRAPH_BREAK for p in processed_page_text]))
    processed_text = "".join(p + PAGE_BREAK for p in processed_text)
    return processed_text


def remove_non_chinese_lines(text: str) -> str:
    page_text = [p for p in text.split(PAGE_BREAK) if p.strip()]
    
    if len(page_text) == 0:
        return ""
    
    filtered_pages = []
    for i in range(len(page_text)):
        paragraphs = [p for p in page_text[i].split(PARAGRAPH_BREAK) if p.strip()]
        filtered_paragraphs = []
        for j in range(len(paragraphs)):
            lines = [line for line in paragraphs[j].split(SENTENCE_BREAK) if line.strip()]
            
            # filter lines in a paragraph are not traditional chinese lines
            filtered_lines = [line for line in lines if is_traditional_chinese_line(line.strip())]
            
            # If paragraph does not just contain not chinese lines
            if filtered_lines:
                filtered_paragraphs.append("".join([line + SENTENCE_BREAK for line in filtered_lines]))
        
        if filtered_paragraphs:
            filtered_pages.append("".join([p+PARAGRAPH_BREAK for p in filtered_paragraphs]))
    
    if filtered_pages:
        filtered_text = "".join([p+PAGE_BREAK for p in filtered_pages])
    else:
        filtered_text = ""
    return filtered_text


def cleanup_extracted_chinese(
    text: str    
) -> str:
    # step 1: Remove lines is not the traditional chinese lines (headers and footers)
    text = remove_non_chinese_lines(text)
    
    # step 2: merge splitted paragraphs
    text = merge_splitted(text)
    
    # step 3: remove sentence break of each line in paragraphs
    text = remove_endline(text)
    
    # step 4: remove all page break in text
    text = text.replace(PAGE_BREAK,"")
    
    processed_text = text
    return processed_text