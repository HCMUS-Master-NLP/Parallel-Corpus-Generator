from bertalign import Bertalign
from typing import Tuple, List, Dict


'''
dict_cps = {id_1: value_1, id_2: value_2, ...}
cs_to_cps_id = [id_1, id_2]
cs_list = [value_1, value_2]
'''
def convert_CPS_to_CS(cps_dict: Dict) -> Tuple[List, List]:
    cs_to_cps_ids = []
    cs_list = []
    for key in cps_dict.keys():
        value = cps_dict[key]
        cs_to_cps_ids.append(key)
        cs_list.append(value)
    return (cs_list, cs_to_cps_ids)


def align_sentences(src: List, tgt: List) -> List:
    '''
        src: Hanzi sentences in a chapter
        tgt: Vietnamese sentences in a chapter
    '''
    src_text = "\n".join(src)
    tgt_text = "\n".join(tgt)

    aligner = Bertalign(src_text, tgt_text, is_split=True, skip=0.0, max_align=6, win=4)
    aligner.align_sents()
    aligner.print_sents()
    
    return aligner.result


def align_section(src_dict: Dict, tgt_list: List, src_id: int):
    src_list, src_dict_keys = convert_CPS_to_CS(src_dict)
    
    results = align_sentences(src_list, tgt_list)
    
    aligned_section = {}
    aligned_section["section_value"] = str(src_id)
    aligned_section["section_content"] = []

    curr_para_id = None
    curr_sent_id = 1
    page_dict = {}
    for bead in results:
        if len(bead[0]) == 0 or len(bead[1]) == 0:
            continue

        src_sent = ' '.join(src_list[bead[0][0]:bead[0][-1]+1])
        tgt_sent = ' '.join(tgt_list[bead[1][0]:bead[1][-1]+1])

        para_id  = int(src_dict_keys[bead[0][0]].split('.')[0])
        
        if curr_para_id == None:
            curr_para_id = para_id
            curr_sent_id = 1
            page_dict = {}
            page_dict["page_value"] = str(curr_para_id)
            page_dict["page_content"] = []
        elif para_id != curr_para_id:
            curr_para_id = para_id
            curr_sent_id = 1
            aligned_section["section_content"].append(page_dict)
            page_dict = {}
            page_dict["page_value"] = str(curr_para_id)
            page_dict["page_content"] = []
            
        sent_dict = {}
        sent_dict["sentence_value"] = str(curr_sent_id)
        sent_dict['sentence_content'] = [src_sent, tgt_sent]

        page_dict["page_content"].append(sent_dict)
        curr_sent_id += 1

    return aligned_section
