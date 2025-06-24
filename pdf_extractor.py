
from typing import Optional, Literal, List
import fitz     # pymupdf
from pathlib import Path
import re

PAGE_BREAK = "\f\n"
PARAGRAPH_BREAK = "\n\n"
SENTENCE_BREAK = "\n"
CHINESE_CHAPTER_TEMPLATE = r"^第[一二三四五六七八九十百千零〇○]+[回囘]"
VIETNAMESE_CHAPTER_TEMPLATE = r"^HỒI THỨ(?: [\wÀ-Ỵ]+)+$"


class PDFTextExtractor:
    def __init__(
        self, 
        file_path: str,
        start_page: int = 1,
        num_pages: Optional[int] = None,
        is_preserve_paragraph: bool = True
    ):
        self.file_path = Path(file_path)
        self.start_page = start_page
        self.num_pages = num_pages
        self.is_preserve_paragraph = is_preserve_paragraph
        self.text = ""
        
    def _extract_text_simple(self):
        with fitz.open(self.file_path) as pdf_file:
            # convert 1-based to 0-based index
            start_idx = max(self.start_page - 1, 0)
            
            if self.num_pages is not None:
                end_idx = min(start_idx + self.num_pages, len(pdf_file))
            else:
                end_idx = len(pdf_file)
            
            text = "".join([
                pdf_file[i].get_text("text") + PAGE_BREAK
                for i in range(start_idx, end_idx)
            ])
        return text

    def _extract_text_preserve_paragraph(self):
        with fitz.open(self.file_path) as pdf:
            start_idx = max(self.start_page - 1, 0)
            end_idx = min(len(pdf), start_idx + self.num_pages) if self.num_pages else len(pdf)
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


class QuocNguPDFExtractor(PDFTextExtractor):
    def __init__(
        self,
        file_path: str,
        start_page: int = 1,
        num_pages: Optional[int] = None
    ):
        super().__init__(file_path, start_page, num_pages, False)
        self.text = self._get_text()
    
    def _get_text(self) -> str:
        text = self._extract_text_simple()
        return self._cleanup_text(text)
        return text
    
    def _add_poem_period(self, text: str) -> str:
        """
            add period at the end of poem sentences
        """
        page_text_list = list(p for p in text.split(PAGE_BREAK) if p.strip())
        processed_page_list = []
        pattern = re.compile(r"^HỒI THỨ(?: [\wÀ-Ỵ]+)+$")
        for page in page_text_list:
            lines = list(l for l in page.split(SENTENCE_BREAK) if l.strip())
            processed_lines = []
            for i, line in enumerate(lines):
                if pattern.match(line.strip()):
                    pass
                elif (len(line.split(' ')) in [4,5,7,6,8]) and (not re.search(r"[.,;:?!]", line[-2:])) and (line.lstrip()[0].isalpha()) and (line.lstrip()[0].isupper()):
                    line = line + '.'        
                processed_lines.append(line)
            processed_page_list.append("".join([line + SENTENCE_BREAK for line in processed_lines]))
        return "".join([p + PAGE_BREAK for p in processed_page_list])

    def _merge_page_break_sentences(self, text: str) -> str:
        page_text_list = [p for p in text.split(PAGE_BREAK) if p.strip()]
        if not page_text_list:
            return ""

        pattern = re.compile(r"^HỒI THỨ(?: [\wÀ-Ỵ]+)+$")
        repaired_page_list = [page_text_list[0]]

        for page in page_text_list[1:]:
            prev_lines = [l for l in repaired_page_list[-1].split(SENTENCE_BREAK) if l.strip()]
            current_lines = [l for l in page.split(SENTENCE_BREAK) if l.strip()]

            if not prev_lines or not current_lines:
                # repaired_page_list.append(page)
                continue

            prev_last_line = prev_lines[-1].rstrip()
            curr_first_line = current_lines[0].lstrip()

            if pattern.match(prev_last_line) or pattern.match(curr_first_line):
                repaired_page_list.append(page)
                continue

            elif len(prev_last_line) >= 1 and not re.search(r"[.;:?!]", prev_last_line[-2:]):
                # Gộp dòng cuối và đầu
                merged = prev_last_line + ' ' + curr_first_line + SENTENCE_BREAK
                repaired_page_list[-1] = "".join([l + SENTENCE_BREAK for l in prev_lines[:-1]]) + merged
                current_lines = current_lines[1:]

            if current_lines:
                repaired_page_list.append("".join([l + SENTENCE_BREAK for l in current_lines]))
        return "".join([p + PAGE_BREAK for p in repaired_page_list])
    
    def _merge_newline_break_sentences(self, text: str) -> str:
        page_text_list = [p for p in text.split(PAGE_BREAK) if p.strip()]
        if not page_text_list:
            return ""

        pattern = re.compile(r"^HỒI THỨ(?: [\wÀ-Ỵ]+)+$")
        repaired_page_list = []

        for page in page_text_list:
            lines = [l for l in page.split(SENTENCE_BREAK) if l.strip()]
            if not lines:
                repaired_page_list.append("")
                continue

            repaired_lines = [lines[0]]
            for i in range(1, len(lines)):
                last_line = repaired_lines[-1].rstrip()
                current_line = lines[i].strip()

                if pattern.match(last_line):
                    repaired_lines.append(current_line)
                elif not re.search(r"[.;:?!]$", last_line):
                    repaired_lines[-1] = last_line + ' ' + current_line
                else:
                    repaired_lines.append(current_line)

            repaired_page_list.append("".join([l + SENTENCE_BREAK for l in repaired_lines]))
        return "".join([p + PAGE_BREAK for p in repaired_page_list])

    def _cleanup_text(self, text: str) -> str:
        text = self._add_poem_period(text)
        text = self._merge_newline_break_sentences(text)
        text = self._merge_page_break_sentences(text)
        text = text.replace(PAGE_BREAK,'')
        return text

    def get_splitted_sections(self, template) -> List:
        sections = []
        section_pattern = re.compile(template)
        lines = [l for l in self.text.split(SENTENCE_BREAK) if l.strip()]
        current_section = []

        for line in lines:
            if section_pattern.match(line.strip()):
                if current_section:
                    sections.append("".join([l+SENTENCE_BREAK for l in current_section]))
                    current_section = []
            current_section.append(line)
        
        if current_section:
            sections.append("".join([l+SENTENCE_BREAK for l in current_section]))

        return sections


class SinoNomPDFExtractor(PDFTextExtractor):
    def __init__(
        self,
        file_path: str,
        start_page: int = 1,
        num_pages: Optional[int] = None,
        is_preserve_paragraph: bool = True
    ):
        super().__init__(file_path,start_page,num_pages,is_preserve_paragraph)
        self.text = self._get_text()
    
    def _get_text(self) -> str:
        if self.is_preserve_paragraph:
            text = self._extract_text_preserve_paragraph()
        else:
            text = self._extract_text_simple()
        # return text
        return self._cleanup_text(text)
    
    def _is_cjk_unified_char(self, ch: str) -> bool:
        return 0x4E00 <= ord(ch) <= 0x9FFF

    def _is_traditional_chinese_line(self, line: str, threshold: float = 0.9) -> bool:
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

    def _remove_non_chinese_lines(self, text) -> str:
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
                filtered_lines = [line for line in lines if self._is_traditional_chinese_line(line.strip())]
                
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

    def _merge_splitted(self, text: str) -> str:
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
                if self._is_likely_continuation(repaired_paragraphs[-1], paragraphs[i]):
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
                if self._is_likely_continuation(prev_paragraphs[-1], curr_paragraphs[0]):
                    prev_paragraphs[-1] = prev_paragraphs[-1] + curr_paragraphs[0]
                    curr_paragraphs = curr_paragraphs[1:]
            
            prev_page = "".join(p + SENTENCE_BREAK + PARAGRAPH_BREAK for p in prev_paragraphs)
            curr_page = "".join(p + SENTENCE_BREAK + PARAGRAPH_BREAK for p in curr_paragraphs)
            
            repaired_pages[-1] = prev_page
            if curr_page.strip():  # add only if curr_page has content
                repaired_pages.append(curr_page)
        
        repaired_pages = "".join(p + PAGE_BREAK for p in repaired_pages)
        return repaired_pages

    def _is_likely_continuation(self, prev_paragraph: str, curr_paragraph: str) -> bool:
        '''check if two paragraphs might be from one paragraph'''
        prev_last_line = [s for s in prev_paragraph.split(SENTENCE_BREAK) if s.strip()][-1]
        curr_first_line = [s for s in curr_paragraph.split(SENTENCE_BREAK) if s.strip()][0]
        
        # Must be the first condition
        if bool(re.search(r"第[一二三四五六七八九十百千萬〇○零]+回", prev_last_line)):
            return False
        
        # if the last character is Han char means paragraph is splitted
        if self._is_cjk_unified_char(prev_last_line[-1]):
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

    def _remove_endline(self, text: str) -> str:
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

    def _cleanup_text(self, text: str) -> str:
        # step 1: Remove lines is not the traditional chinese lines (headers and footers)
        text = self._remove_non_chinese_lines(text)
        
        # step 2: merge splitted paragraphs
        # text = self._merge_splitted(text)
        text = self._merge_newline_break_paragraph(text)
        text = self._merge_page_break_sentences(text)
        
        # step 3: remove sentence break of each line in paragraphs
        # text = self._remove_endline(text)
        
        # step 4: remove all page break in text
        text = text.replace(PAGE_BREAK,"")

        processed_text = text
        return processed_text
      
    def _merge_page_break_sentences(self, text: str) -> str:
        page_text_list = [p for p in text.split(PAGE_BREAK) if p.strip()]
        if not page_text_list:
            return ""

        pattern = re.compile(r"^第[一二三四五六七八九十百千零〇○]+[回囘]")
        repaired_page_list = [page_text_list[0]]

        for page in page_text_list[1:]:
            prev_paragraphs = [p for p in repaired_page_list[-1].split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]
            curr_paragraphs = [p for p in page.split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]

            if not prev_paragraphs or not curr_paragraphs:
                repaired_page_list.append(page)
                continue

            prev_last_para = prev_paragraphs[-1].rstrip()
            curr_first_para = curr_paragraphs[0].lstrip()

            if pattern.match(prev_last_para) or pattern.match(curr_first_para):
                repaired_page_list.append(page)
                continue

            if self._is_likely_continuation(prev_last_para, curr_first_para):
                repaired_page_list[-1] = repaired_page_list[-1].rstrip() + curr_first_para.strip() + SENTENCE_BREAK + PARAGRAPH_BREAK
                curr_paragraphs = curr_paragraphs[1:]
                repaired_page_list.append("".join([p.rstrip() + SENTENCE_BREAK + PARAGRAPH_BREAK for p in curr_paragraphs]))
            else:
                repaired_page_list.append(page)

        return "".join([p + PAGE_BREAK for p in repaired_page_list])
    
    def _merge_newline_break_paragraph(self, text: str) -> str:
        page_text_list = [p for p in text.split(PAGE_BREAK) if p.strip()]
        if not page_text_list:
            return ""

        pattern = re.compile(r"^第[一二三四五六七八九十百千零〇○]+[回囘]")
        repaired_page_list = []
        for page in page_text_list:
            paragraphs = [p for p in page.split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]

            # if page is null
            if not paragraphs:
                continue
            
            repaired_paragraphs = [paragraphs[0]]
            for para in paragraphs[1:]:
                # if title in paragraph, then not merge
                if pattern.match(repaired_paragraphs[-1]):
                    repaired_paragraphs.append(para)
                    continue
                
                # if prev paragraph is likely connect with current paragraph, then merge, else not merge
                if self._is_likely_continuation(repaired_paragraphs[-1], para):
                   repaired_paragraphs[-1] = repaired_paragraphs[-1].rstrip() + para 
                else:
                    repaired_paragraphs.append(para)
            
            repaired_page_list.append("".join([p.rstrip() + SENTENCE_BREAK + PARAGRAPH_BREAK for p in repaired_paragraphs]))

        return "".join([p + PAGE_BREAK for p in repaired_page_list])

    # def _merge_newline_break_sentences(self, text: str) -> str:
    #     page_text_list = [p for p in text.split(PAGE_BREAK) if p.strip()]
    #     if not page_text_list:
    #         return ""

    #     pattern = re.compile(r"^第[一二三四五六七八九十百千零〇○]+[回囘]")
    #     repaired_page_list = []

    #     for page in page_text_list:
    #         paragraphs = [p for p in page.split(SENTENCE_BREAK + PARAGRAPH_BREAK) if p.strip()]
    #         repaired_para_list = []
    #         for para in paragraphs:
    #             lines = [l for l in para.split(SENTENCE_BREAK) if l.strip()]            
    #     return "".join([p + PAGE_BREAK for p in repaired_page_list])

    def get_splitted_sections(self, template) -> List:
        section_pattern = re.compile(template)
        paragraphs = [l for l in self.text.split(SENTENCE_BREAK + PARAGRAPH_BREAK) if l.strip()]
        sections = []
        current_section = []
        for para in paragraphs:
            lines = [l for l in para.split(SENTENCE_BREAK) if l.strip()]
            if section_pattern.match(lines[0]):
                if current_section:
                    sections.append("".join([p.rstrip() + SENTENCE_BREAK + PARAGRAPH_BREAK for p in current_section]))
                    current_section = []

            current_section.append(para)
        
        if current_section:
            sections.append("".join([p.rstrip() + SENTENCE_BREAK + PARAGRAPH_BREAK for p in current_section]))

        return sections
        # sections = []
        # section_pattern = re.compile(template)
        # lines = [l for l in self.text.split(PARAGRAPH_BREAK) if l.strip()]
        # current_section = []

        # for line in lines:
        #     if section_pattern.match(line):
        #         if current_section:
        #             sections.append("".join([l+PARAGRAPH_BREAK for l in current_section]))
        #             current_section = []
        #     current_section.append(line)
        
        # if current_section:
        #     sections.append("".join([l+PARAGRAPH_BREAK for l in current_section]))

        # return sections