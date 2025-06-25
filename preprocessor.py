
import re
from pathlib import Path
from typing import List
import unicodedata
# from opencc import OpenCC

from quocngu_normalizer.text_cleaner import TextCleaner


class QuocNguPreprocessor:
    def __init__(self, config_path=None):
        self.cleaner = TextCleaner(config_path=Path(config_path))
    
    def normalize(self, text: str) -> str:
        norm_text = self.cleaner.clean_text(text)
        return norm_text
    
    def split_sents(self, text: str) -> List:
        """
        Split a Vietnamese text into sentences.
        Uses regex to identify sentence boundaries based on punctuation marks.
        """
        if not text.strip():
            return []

        # Remove extra whitespace and normalize the text
        text = re.sub(r'\s+', ' ', text.strip())

        # Define sentence ending patterns for Vietnamese text
        sentence_endings = r'[.!?…]+'

        # Split by sentence endings and keep the punctuation
        parts = re.split(f'({sentence_endings})', text)

        result = []
        current_sentence = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if re.match(f'^{sentence_endings}$', part):
                # This is sentence ending
                current_sentence += part
                if current_sentence.strip():
                    result.append(current_sentence.strip())
                current_sentence = ""
            else:
                # This is text
                current_sentence += part

        # Add any remaining sentence
        if current_sentence.strip():
            result.append(current_sentence.strip())

        # Filter out very short sentences (likely fragments)
        result = [s for s in result if len(s.strip()) > 2]

        return result

    def norm_and_split_sents(self, text: str) -> List:
        norm_text = self.normalize(text)
        return self.split_sents(norm_text)


class SinoNomPreprocessor:
    def __init__(self, config=None):
        self.para_break = '\n\n' if not config else config.PARAGRAPH_BREAK

    def normalize(self, text: str) -> str:
        """
        Chuẩn hóa văn bản tiếng Trung bao gồm:
        - Chuẩn hóa Unicode
        - Chuyển đổi dấu câu và mã ký tự
        - Chuyển đổi giản thể ↔ phồn thể
        - Loại bỏ ký tự nhiễu (HTML, markdown, chú thích, ...)
        - Giữ lại ký tự CJK và dấu câu tiếng Trung phổ biến
        - Chuẩn hóa dấu câu lặp và định dạng ngoặc kép

        Args:
            text (str): Văn bản đầu vào cần chuẩn hóa
            to_traditional (bool):
                - True: chuyển văn bản về **phồn thể**
                - False (default): chuyển về **giản thể**

        Returns:
            str: Văn bản đã được chuẩn hóa

        Các bước xử lý cụ thể:
        1. Chuẩn hóa mã Unicode theo chuẩn NFKC
        2. Chuyển đổi ký tự full-width → half-width (dấu tiếng Trung thành ASCII)
        3. Chuyển đổi chữ Giản thể ↔ Phồn thể bằng OpenCC
        4. Xóa các yếu tố nhiễu như:
        - Thẻ HTML (`<...>`)
        - Chú thích dạng `[1]`, `【注】`
        - Markdown `#title`
        5. Giữ lại các ký tự tiếng Trung, khoảng trắng, và dấu câu chuẩn (`。，！？：「」『』—…·《》`)
        6. Chuẩn hóa khoảng trắng, loại bỏ dấu câu bị lặp
        7. Thay thế ngoặc kép tiếng Trung:
        - 「」 → “”
        - 『』 → “”
        """
        # 1. Normalize Unicode (NFKC)
        text = text.replace(']', '」')
        text = unicodedata.normalize("NFKC", text)

        # 2. Convert full-width → half-width
        text = ''.join(
            chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c
            for c in text
        )

        # 3. Convert Simplified ↔ Traditional
        # if to_traditional:
        #     text = OpenCC('s2t').convert(text)
        # else:
        #     text = OpenCC('t2s').convert(text)

        # 4. Remove noise (HTML tags, markdown, [1], 【注】)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        text = re.sub(r'【[^】]*】', '', text)
        text = re.sub(r'#.*', '', text)
        text = text.replace(',', '，')

        # 5. Filter only CJK characters + standard punctuations
        text = ''.join(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef。，、！? :「」『』—…·《》\s]+', text))

        # 6. Normalize spacing and repeated punctuation 
        text = re.sub(r'\s+', '', text)  # Remove all whitespaces
        text = re.sub(r'([，。！? :「」『』—…·])\1+', r'\1', text)
        text = text.replace('「', '“').replace('」', '”')
        text = text.replace('『', '“').replace('』', '”')
        text = text.strip()

        return text

    def split_sents(self, text) -> List:
        """
        Tách văn bản tiếng Hán thành từng câu hoàn chỉnh.

        Quy tắc tách:
        - Tách câu khi gặp dấu kết thúc câu: 。！？ (kèm hoặc không kèm dấu ngoặc kép ”)
        - Nếu dấu kết thúc là 。！？ rồi đến ” (ví dụ: ？”), thì tách sau dấu ”
        - Nếu chỉ là 。！？ và không có ” theo sau, thì tách ngay sau dấu đó
        - Không làm mất dấu câu hoặc dấu ngoặc kép
        - Câu phía sau sẽ được giữ nguyên nội dung

        Args:
            text (str): Văn bản tiếng Hán cần tách câu

        Returns:
            List[str]: Danh sách các câu đã tách, được loại bỏ khoảng trắng dư thừa

        Cách hoạt động:
        - Bước 1: Dùng re.sub() để chèn dấu phân cách đặc biệt (###) sau dấu kết câu
                với điều kiện: nếu sau dấu đó là ” → chèn sau ”
        - Bước 2: Với các dấu câu không có ” sau → chèn ngay sau dấu câu
        - Bước 3: Dùng .split('###') để phân chia văn bản thành các câu riêng biệt
        - Bước 4: Xoá khoảng trắng dư và lọc bỏ chuỗi rỗng
        """
        # Thêm dấu phân cách đặc biệt sau dấu kết thúc câu để tách
        text = re.sub(r'([。！?])”(?=\S)', r'\1”###', text)
        text = re.sub(r'([。！?])(?![”])(?=\S)', r'\1###', text)

        # Tách theo dấu ###
        sentences = text.split('###')
        
        return [s.strip() for s in sentences if s.strip()]

    def norm_and_split_sents(self, sect_text: str) -> List:
        # paragraph splitting
        paragraph_section_text = [s for s in sect_text.split(self.para_break) if s.strip()]
        
        # normalization
        norm_para_section_text = []
        for p in paragraph_section_text:
            norm_para_section_text.append(self.normalize(p))

        # sentence splitting
        sentence_para_section_text = []
        for p in norm_para_section_text:
            sentence_para_section_text.append(self.split_sents(p))
        
        return sentence_para_section_text

