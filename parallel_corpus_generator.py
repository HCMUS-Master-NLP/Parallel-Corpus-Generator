
import re
from typing import List, Dict, Optional
from pathlib import Path
import json
from underthesea import word_tokenize

from config import GeneratorConfig, LoggerMixin
from pdf_extractor import SinoNomPDFExtractor, QuocNguPDFExtractor
from preprocessor import QuocNguPreprocessor, SinoNomPreprocessor
from bertalign import Bertalign
from xml_builder import XMLBuilder


class ParallelCorpusGenerator(LoggerMixin):
    def __init__(self, config: GeneratorConfig):
        super().__init__(logger_name=self.__class__.__name__, log_level=config.log_level)        
        self.config = config

        self.sinonom_pdf_extractor = SinoNomPDFExtractor(
            file_path=self.config.sinonom_pdf_path, 
            start_page=self.config.sinonom_start_page, 
            num_pages=self.config.sinonom_num_pages)
        
        self.quocngu_pdf_extractor = QuocNguPDFExtractor(
            file_path=self.config.quocngu_pdf_path, 
            start_page=self.config.quocngu_start_page, 
            num_pages=self.config.quocngu_num_pages)

        self.sinonom_preprocessor = SinoNomPreprocessor(config = self.config)
        self.quocngu_preprocessor = QuocNguPreprocessor(config_path = Path(self.config.noise_json_path))

        self.sinonom_sections = {}
        self.quocngu_sections = {}
        
        self.quocngu_section_names = {}

        self._extract_sections()

    def _split_quocngu_sections(self, text) -> Dict:
        section_pattern = re.compile(self.config.QUOCNGU_SECTION_TEMPLATE)
        lines = [l for l in text.split(self.config.SENTENCE_BREAK) if l.strip()]
        
        sect_dict = {}
        current_section = []
        curr_sect_id = ""
        curr_sect_name = ""

        for line in lines:
            if section_pattern.match(line.strip()):
                if current_section:
                    self.quocngu_section_names[str(curr_sect_id)] = curr_sect_name
                    sect_dict[str(curr_sect_id)] = "".join([l + self.config.SENTENCE_BREAK for l in current_section])
                    current_section = []

                curr_sect_name = section_pattern.search(line.strip()).group(0)
                curr_sect_id = self._extract_quocngu_section_number(line)
            
            current_section.append(line)
        
        if current_section:
            self.quocngu_section_names[str(curr_sect_id)] = curr_sect_name
            sect_dict[str(curr_sect_id)] = "".join([l + self.config.SENTENCE_BREAK for l in current_section])
        return sect_dict

    def _split_sinonom_sections(self, text) -> Dict:
        section_pattern = re.compile(self.config.SINONOM_SECTION_TEMPLATE)
        paragraphs = [l for l in text.split(self.config.SENTENCE_BREAK + self.config.PARAGRAPH_BREAK) if l.strip()]
        section_dict = {}
        current_section = []
        curr_sect_id = ""

        for para in paragraphs:
            lines = [l for l in para.split(self.config.SENTENCE_BREAK) if l.strip()]
            if section_pattern.match(lines[0]):
                if len(current_section) != 0:
                    section_dict[curr_sect_id] = "".join([p.rstrip() + self.config.SENTENCE_BREAK + self.config.PARAGRAPH_BREAK for p in current_section])
                    current_section = []
                curr_sect_id = str(self._extract_sinonom_section_number(para))
            current_section.append(para)

        if current_section:
            section_dict[curr_sect_id] = "".join([p.rstrip() + self.config.SENTENCE_BREAK + self.config.PARAGRAPH_BREAK for p in current_section])
        return section_dict

    def _extract_sections(self) -> None:
        self.sinonom_sections = self._split_sinonom_sections(self.sinonom_pdf_extractor.text)
        if self.config.verbose: 
            end_page = self.config.sinonom_start_page + self.config.sinonom_num_pages - 1
            self.logger.info(f"Successfully extracted text from page {self.config.sinonom_start_page} to {end_page} from SinoNom PDF text.")

        self.quocngu_sections = self._split_quocngu_sections(self.quocngu_pdf_extractor.text)
        if self.config.verbose: 
            end_page = self.config.quocngu_start_page + self.config.quocngu_num_pages - 1
            self.logger.info(f"Successfully extracted text from page {self.config.quocngu_start_page} to {end_page} from Vietnamese PDF text.")

    def align_and_save_sections(self, sect_ids: Optional[List] = None):
        for sect_id in sect_ids:
            sect_id = str(sect_id)
            if sect_id in self.sinonom_sections.keys() and sect_id in self.quocngu_sections.keys():
                sinonom_section = self.sinonom_preprocessor.norm_and_split_sents(self.sinonom_sections[sect_id])
                sinonom_sentence_list, sinonom_para_ids = self._flatten_section_with_para_ids(sinonom_section)

                quocngu_sentence_list = self.quocngu_preprocessor.norm_and_split_sents(self.quocngu_sections[sect_id])

                sinonom_sentence_text = '\n'.join(sinonom_sentence_list)
                quocngu_sentence_text = '\n'.join(quocngu_sentence_list)

                aligner = Bertalign(
                    sinonom_sentence_text, 
                    quocngu_sentence_text, 
                    self.config.align_options['max_align'],
                    self.config.align_options['top_k'],
                    self.config.align_options['win'],
                    self.config.align_options['skip'],
                    self.config.align_options['margin'],
                    self.config.align_options['len_penalty'],
                    self.config.align_options['is_split'])
                aligner.align_sents()
        
                if self.config.verbose: 
                    self.logger.info(f"Successfully align SinoNom-Vietnamese text from section {sect_id}.")
                
                self._save_aligned_section(
                    sect_id,
                    sinonom_sentence_list,
                    quocngu_sentence_list,
                    aligner.result,
                    sinonom_para_ids)
    
    def _clean_chinese_text(self, text):
        # Danh sách dấu câu và ký hiệu cần loại bỏ
        punctuation_pattern = r'[ 。，、；：？！…—·．「」『』“”‘’（）〈〉《》【】［］〔〕＼／—~@#$%^&*+=<>`|:?]'
        
        # Xoá dấu
        cleaned = re.sub(punctuation_pattern, '', text)
        return cleaned
    
    def _is_vietnamese_word(self, token):
        # Giữ token chỉ gồm các chữ cái, chữ số (kể cả có dấu)
        return re.fullmatch(r"[A-Za-zÀ-ỹà-ỹĐđ1-9_]+", token) is not None
    
    def _save_stat_section(
        self, 
        sect_id, 
        pairs,
    ):
        ''' Format:
            {
                "num_pairs": int,
                "num_paragraphs": int,
                "paragraph_length_list": List,
                "vietnamese":{
                    "sentence_length_list": List,
                    "unique_token_list": List
                },
                "chinese":{
                    "sentence_length_list": List,
                    "unique_token_list": List
                }
            }
        '''
        stat = {}
        para_length_list = []
        
        token_dict = {}
        token_dict['chinese'] = []
        token_dict['vietnamese'] = []
        
        sent_length_dict = {}
        sent_length_dict['chinese'] = []
        sent_length_dict['vietnamese'] = []
        
        for para_pairs in pairs:
            para_length_list.append(len(para_pairs))
            for chinese_sent, vietnamese_sent in para_pairs:
                vietnamese_token_list = [token.lower() for token in word_tokenize(vietnamese_sent, format='text').split() if self._is_vietnamese_word(token)]
                sent_length_dict['vietnamese'].append(len(vietnamese_token_list))
                token_dict['vietnamese'].extend(vietnamese_token_list)
                
                chinese_token_list = list(self._clean_chinese_text(chinese_sent))
                sent_length_dict['chinese'].append(len(chinese_token_list))
                token_dict['chinese'].extend(chinese_token_list)
                
        stat['num_pairs'] = sum(para_length_list)
        stat['num_paragraphs'] = len(pairs)
        stat['paragraph_length_list'] = para_length_list
        
        stat['vietnamese'] = {}
        stat['vietnamese']['sentence_length_list'] = sent_length_dict['vietnamese']
        stat['vietnamese']['unique_token_list'] = list(set(token_dict['vietnamese'])) 
        stat['chinese'] = {}
        stat['chinese']['sentence_length_list'] = sent_length_dict['chinese']
        stat['chinese']['unique_token_list'] = list(set(token_dict['chinese'])) 
        
        output_folder = Path(self.config.output_folder_path) / "aligned_section_stat"
        output_folder.mkdir(parents=True, exist_ok=True)
        file_path = output_folder / f"{sect_id}.json" 
        
        if file_path.exists():
            file_path.unlink()
            
        with open(file_path, "w", encoding='utf-8') as fp:
            json.dump(stat, fp, ensure_ascii=False)
            
        if self.config.verbose: self.logger.info(f"Successfully save statistics of aligned section {sect_id} in {file_path}")
                     
    def _save_aligned_section(
        self, 
        sect_id, 
        sinonom_sentences, 
        quocngu_sentences, 
        align_result, 
        sinonom_para_ids
    ) -> None:
        # Save aligned section to XML
        xml_builder = XMLBuilder(
            file = self.config.xml_metadata['file id'],
            title = self.config.xml_metadata['title'],
            volume = self.config.xml_metadata['volume'],
            author = self.config.xml_metadata['author'],
            period = self.config.xml_metadata['period'],
            language = self.config.xml_metadata['language'],
            translator = self.config.xml_metadata['translator'],
            source = self.config.xml_metadata['source']
        )
        para_list = []
        pairs = []
        curr_para_id = ""
        curr_pairs = []
        for bead in align_result:
            if len(bead[0]) == 0 or len(bead[1]) == 0:
                continue
            sinonom_sent = self._get_sent(bead[0], sinonom_sentences)
            quocngu_sent = self._get_sent(bead[1], quocngu_sentences)
            if curr_para_id != sinonom_para_ids[int(bead[0][0])]:
                if curr_pairs:
                    pairs.append(curr_pairs)
                    para_list.append(curr_para_id)
                    curr_pairs = []
                curr_para_id = sinonom_para_ids[int(bead[0][0])]
            curr_pairs.append([sinonom_sent, quocngu_sent])

        if curr_pairs:
            pairs.append(curr_pairs)
            para_list.append(curr_para_id)

        sect_name = self.quocngu_section_names[sect_id]
        output_dir = Path(self.config.output_folder_path) / "aligned_section_xml"
        
        # delete file if it exists
        output_file = output_dir / f"{sect_id}.xml"
        if output_file.exists():
            output_file.unlink()

        xml_builder.add_pair_sentence(
            sect_id=sect_id,
            sect_name=sect_name,
            pairs = pairs,
            paragraphs_lst = para_list)
        xml_builder.save(output_name=f"{sect_id}.xml", output_dir=output_dir)
        if self.config.verbose: self.logger.info(f"Successfully save aligned SinoNom-Vietnamese section {sect_id} to {output_file}.")
        
        self._save_stat_section(sect_id, pairs)
        self._save_raw_aligned_section(sect_id, sinonom_sentences, quocngu_sentences, align_result)

    def _save_raw_aligned_section(
        self, 
        sect_id, 
        sinonom_sentences, 
        quocngu_sentences, 
        align_result, 
    ):
        text = ""
        for bead in align_result:
            text = text + self._get_sent(bead[0], sinonom_sentences) + '\n'
            text = text + self._get_sent(bead[1], quocngu_sentences) + '\n'
            text = text + '\n'
        
        output_folder = Path(self.config.output_folder_path) / "raw_aligned_section"
        output_folder.mkdir(parents=True, exist_ok=True)
        file_path = output_folder / f"{sect_id}.txt" 
        
        if file_path.exists():
            file_path.unlink()
            
        with open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(text)
        if self.config.verbose: self.logger.info(f"Successfully save raw aligned section {sect_id} in {file_path}")
             
    def _get_sent(self, bead, sent_list) -> str:
        if len(bead) != 0:
            sent = ' '.join(sent_list[bead[0]:bead[-1]+1])
            return sent
        else:
            return ''

    def _flatten_section_with_para_ids(self, section):
        '''
            input: section = [[para_0_sent_1, para_0_sent_2],...]
            output: sentence_list = [para_0_sent_1, para_0_sent_2, ...]
                    para_id_list = []
        '''
        flattened = []
        para_ids = []
        for para_idx, sentences in enumerate(section):
            flattened.extend(sentences)
            para_ids.extend([para_idx] * len(sentences))
        return flattened, para_ids

    def _extract_sinonom_section_number(self, section):
        # Tìm dòng bắt đầu bằng "HỒI THỨ", sau đó lấy phần chữ phía sau
        match = re.search(self.config.SINONOM_SECTION_TEMPLATE, section, re.MULTILINE)
        if match:
            return self._chinese_to_number(match.group(1).strip())
        return -1

    def _extract_quocngu_section_number(self, section):
        # Tìm dòng bắt đầu bằng "HỒI THỨ", sau đó lấy phần chữ phía sau
        match = re.search(self.config.QUOCNGU_SECTION_TEMPLATE, section, re.MULTILINE)
        if match:
            return self._vietnamese_to_number(match.group(1).strip())
        return -1

    def _vietnamese_to_number(self, vietnamese: str) -> int:
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

    def _chinese_to_number(self, hanzi: str) -> int:
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
