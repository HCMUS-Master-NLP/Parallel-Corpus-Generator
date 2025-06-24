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

    # src_dict = {
    #     "TDK_001.001.001.01": "蓋聞天地之數,有十二萬九千六百歲為一元.",
    #     "TDK_001.001.001.02": "將一元分為十二會,乃子、丑、寅 、卯、辰、巳、午、未、申、酉、戌、亥之十二支也.",
    #     "TDK_001.001.001.03": "每會該一萬八百歲.",
    #     "TDK_001.001.001.04": "且就 一日而論:子時得陽氣,而丑則雞鳴;",
    #     "TDK_001.001.001.05": "寅不通光,而卯則日出;",
    #     "TDK_001.001.001.06": "辰時食後,而巳 則挨排;",
    #     "TDK_001.001.001.07": "日午天中,而未則西蹉;",
    #     "TDK_001.001.001.08": "申時晡,而日落酉,戌黃昏,而人定亥.",
    #     "TDK_001.001.001.09": "譬於 大數,若到戌會之終,則天地昏曚而萬物否矣.",
    #     "TDK_001.001.001.10": "再去五千四百歲,交亥會之初, 則當黑暗,而兩間人物俱無矣,故曰混沌."}
    
    # tgt_list = ["Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên.",
    #             "Một nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.",
    #             "Mỗi một hội là mười nghìn tám trăm năm.",
    #             "Lại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy.",
    #             "Giờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc.",
    #             "Giờ Thìn ăn cơm xong, thì giờ Tỵ đã liền kề.",
    #             "Giờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây.",
    #             "Giờ Thân là lúc mặt trời lặn ở phương tây.",
    #             "Giờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ.",
    #             "So trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ.",
    #             "Vào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn.",
    #             "Trải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết.",
    #             "Hết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ."]

    src_list, src_dict_keys = convert_CPS_to_CS(src_dict)
    # print(src_list)
    # print(tgt_list)

    results = align_sentences(src_list, tgt_list)
    
    aligned_section = {}
    aligned_section["section_value"] = src_id
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
            page_dict["page_value"] = curr_para_id
            page_dict["page_content"] = []
        elif para_id != curr_para_id:
            curr_para_id = para_id
            curr_sent_id = 1
            aligned_section["section_content"].append(page_dict)
            page_dict = {}
            page_dict["page_value"] = curr_para_id
            page_dict["page_content"] = []
            
        sent_dict = {}
        sent_dict["sentence_value"] = curr_sent_id
        sent_dict['sentence_content'] = [src_sent, tgt_sent]

        page_dict["page_content"].append(sent_dict)
        curr_sent_id += 1

    return aligned_section
