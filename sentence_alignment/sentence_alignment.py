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

    aligner = Bertalign(src_text, tgt_text, is_split=True, skip=-0.1, max_align=2)

    tgt_cs_list = ["" for _ in range(len(src))]
    aligner.align_sents()
    print(aligner.result)
    for (src_id, tgt_ids) in aligner.result:
        if len(src_id):
        # src_line = aligner.src_sents[src_id]
            tgt_line = "".join(tgt_sent for tgt_sent in aligner.tgt_sents[tgt_ids[0]:tgt_ids[-1]+1])
            tgt_cs_list[src_id[0]] = tgt_line
    return tgt_cs_list


def align_chapters(src_folder: str, tgt_folder: str):

    src_dict = {
        "TDK_001.001.001.01": "蓋聞天地之數,有十二萬九千六百歲為一元.",
        "TDK_001.001.001.02": "將一元分為十二會,乃子、丑、寅 、卯、辰、巳、午、未、申、酉、戌、亥之十二支也.",
        "TDK_001.001.001.03": "每會該一萬八百歲.",
        "TDK_001.001.001.04": "且就 一日而論:子時得陽氣,而丑則雞鳴;",
        "TDK_001.001.001.05": "寅不通光,而卯則日出;",
        "TDK_001.001.001.06": "辰時食後,而巳 則挨排;",
        "TDK_001.001.001.07": "日午天中,而未則西蹉;",
        "TDK_001.001.001.08": "申時晡,而日落酉,戌黃昏,而人定亥.",
        "TDK_001.001.001.09": "譬於 大數,若到戌會之終,則天地昏曚而萬物否矣.",
        "TDK_001.001.001.10": "再去五千四百歲,交亥會之初, 則當黑暗,而兩間人物俱無矣,故曰混沌."}
    
    tgt_list = ["Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên.",
                "Một nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi.",
                "Mỗi một hội là mười nghìn tám trăm năm.",
                "Lại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy.",
                "Giờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc.",
                "Giờ Thìn ăn cơm xong, thì giờ Tỵ đã liền kề.",
                "Giờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây.",
                "Giờ Thân là lúc mặt trời lặn ở phương tây.",
                "Giờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ.",
                "So trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ.",
                "Vào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn.",
                "Trải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết.",
                "Hết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ."]

    src_list, src_dict_keys = convert_CPS_to_CS(src_dict)

    tgt_to_src_list = align_sentences(src_list, tgt_list)
    for i in range(len(src_list)):
        print(f"{src_dict_keys[i]}:\n{src_list[i]}\n{tgt_to_src_list[i]}",end="\n\n")


if __name__=="__main__":
    # src = ["蓋聞天地之數,有十二萬九千六百歲為一元。將一元分為十二會,乃子、丑、寅 、卯、辰、巳、午、未、申、酉、戌、亥之十二支也。每會該一萬八百歲。且就 一日而論:子時得陽氣,而丑則雞鳴;寅不通光,而卯則日出;辰時食後,而巳 則挨排;日午天中,而未則西蹉;申時晡,而日落酉,戌黃昏,而人定亥。譬於 大數,若到戌會之終,則天地昏曚而萬物否矣。再去五千四百歲,交亥會之初, 則當黑暗,而兩間人物俱無矣,故曰混沌。又五千四百歲,亥會將終,貞下起元 ,近子之會,而復逐漸開明。邵康節曰::「冬至子之半,天心無改移。一陽初 動處,萬物未生時。」到此,天始有根。再五千四百歲,正當子會,輕清上騰, 有日,有月,有星,有辰。日、月、星、辰,謂之四象。故曰,天開於子。又經 五千四百歲,子會將終,近丑之會,而逐漸堅實。《易》曰:「大哉乾元!至哉坤元!萬物資生,乃順承天。」至此,地始凝結。再五千四百歲,正當丑會,重 濁下凝,有水,有火,有山,有石,有土。水、火、山、石、土,謂之五形。故 曰,地闢於丑。又經五千四百歲,丑會終而寅會之初,發生萬物。曆曰:「天氣 下降,地氣上升;天地交合,群物皆生。」至此,天清地爽,陰陽交合。再五千 四百歲,子會將終,近丑之會,而逐漸堅實。《易》曰:「大哉乾元!至哉坤元 !萬物資生,乃順承天。」至此,地始凝結。再五千四百歲,正當丑會,重濁下 凝,有水,有火,有山,有石,有土。水、火、山、石、土,謂之五形。故曰, 地闢於丑。又經五千四百歲,丑會終而寅會之初,發生萬物。曆曰:「天氣下降 ,地氣上升;天地交合,群物皆生。」至此,天清地爽,陰陽交合。再五千四百 歲,正當寅會,生人,生獸,生禽,正謂天地人,三才定位。故曰,人生於寅。"]
    # tgt = ["Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên. Một nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi. Mỗi một hội là mười nghìn tám trăm năm. Lại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy. Giờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc. Giờ Thìn ăn cơm xong, thì giờ Tỵ đã liền kề. Giờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây. Giờ Thân là lúc mặt trời lặn ở phương tây. Giờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ. So trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ. Vào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn. Trải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết. Hết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ. Thiệu Khang Tiết nói: “Giữa giờ Tý đông chí, Lòng trời chẳng đổi dời Lúc một dương lay động Vạn vật chưa ra đời” Đến đây, trời bắt đầu có rễ. Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Tý, những thứ nhẹ trong bay lên, có mặt trời, mặt trăng, tinh tú. Mặt trời, mặt trăng tinh tú (tinh và thần) gọi là tứ tượng. Cho nên nói rằng: trời mở ở Tý. Lại trải qua năm nghìn bốn trăm năm, hội Tý sắp hết, gần sang hội Sửu, thì dần dần rắn chắc. Kinh dịch nói: “Lớn thay đức nguyên của quẻ Càn! Tuyệt thay đức nguyên của kẻ khôn! Vạn vật nhờ đó sinh ra, là thuận theo trời”. Đến đây đất bắt đầu ngưng kết. Lại trải qua bốn nghìn năm trăm năm, đúng vào hội Sửu, những thứ nặng đục ngưng xuống. Có nước, có lửa, có núi, có đá, có đất. Nước, lửa, núi, đá, đất gọi là ngũ hình. Cho nên nói rằng: Đất mở ở Sửu. Lại trải qua năm nghìn bốn trăm năm, hội Sửu hết, hội Dần bất đầu, muôn vật sinh ra. Sách Lịch nói: “Khí trời bay xuống, khí đất bốc lên trời đất giao hòa, muôn vật sinh ra”. Đến đây trời, đất sáng sủa, âm dương giao hòa, Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Dần, sinh người, sinh thú, sinh chim, gọi là tam tài, gồm trời, đất, người định vị. Cho nên nói rằng: người sinh ra ở Dần."]
    # src = "蓋聞天地之數,有十二萬九千六百歲為一元。將一元分為十二會,乃子、丑、寅 、卯、辰、巳、午、未、申、酉、戌、亥之十二支也。每會該一萬八百歲。且就 一日而論:子時得陽氣,而丑則雞鳴;寅不通光,而卯則日出;辰時食後,而巳 則挨排;日午天中,而未則西蹉;申時晡,而日落酉,戌黃昏,而人定亥。譬於 大數,若到戌會之終,則天地昏曚而萬物否矣。再去五千四百歲,交亥會之初, 則當黑暗,而兩間人物俱無矣,故曰混沌。又五千四百歲,亥會將終,貞下起元 ,近子之會,而復逐漸開明。邵康節曰::「冬至子之半,天心無改移。一陽初 動處,萬物未生時。」到此,天始有根。再五千四百歲,正當子會,輕清上騰, 有日,有月,有星,有辰。日、月、星、辰,謂之四象。故曰,天開於子。又經 五千四百歲,子會將終,近丑之會,而逐漸堅實。《易》曰:「大哉乾元!至哉坤元!萬物資生,乃順承天。」至此,地始凝結。再五千四百歲,正當丑會,重 濁下凝,有水,有火,有山,有石,有土。水、火、山、石、土,謂之五形。故 曰,地闢於丑。又經五千四百歲,丑會終而寅會之初,發生萬物。曆曰:「天氣 下降,地氣上升;天地交合,群物皆生。」至此,天清地爽,陰陽交合。再五千 四百歲,子會將終,近丑之會,而逐漸堅實。《易》曰:「大哉乾元!至哉坤元 !萬物資生,乃順承天。」至此,地始凝結。再五千四百歲,正當丑會,重濁下 凝,有水,有火,有山,有石,有土。水、火、山、石、土,謂之五形。故曰, 地闢於丑。又經五千四百歲,丑會終而寅會之初,發生萬物。曆曰:「天氣下降 ,地氣上升;天地交合,群物皆生。」至此,天清地爽,陰陽交合。再五千四百 歲,正當寅會,生人,生獸,生禽,正謂天地人,三才定位。故曰,人生於寅。"
    # tgt = "Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên. Một nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi. Mỗi một hội là mười nghìn tám trăm năm. Lại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy. Giờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc. Giờ Thìn ăn cơm xong, thì giờ Tỵ đã liền kề. Giờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây. Giờ Thân là lúc mặt trời lặn ở phương tây. Giờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ. So trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ. Vào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn. Trải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết. Hết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ. Thiệu Khang Tiết nói: “Giữa giờ Tý đông chí, Lòng trời chẳng đổi dời Lúc một dương lay động Vạn vật chưa ra đời” Đến đây, trời bắt đầu có rễ. Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Tý, những thứ nhẹ trong bay lên, có mặt trời, mặt trăng, tinh tú. Mặt trời, mặt trăng tinh tú (tinh và thần) gọi là tứ tượng. Cho nên nói rằng: trời mở ở Tý. Lại trải qua năm nghìn bốn trăm năm, hội Tý sắp hết, gần sang hội Sửu, thì dần dần rắn chắc. Kinh dịch nói: “Lớn thay đức nguyên của quẻ Càn! Tuyệt thay đức nguyên của kẻ khôn! Vạn vật nhờ đó sinh ra, là thuận theo trời”. Đến đây đất bắt đầu ngưng kết. Lại trải qua bốn nghìn năm trăm năm, đúng vào hội Sửu, những thứ nặng đục ngưng xuống. Có nước, có lửa, có núi, có đá, có đất. Nước, lửa, núi, đá, đất gọi là ngũ hình. Cho nên nói rằng: Đất mở ở Sửu. Lại trải qua năm nghìn bốn trăm năm, hội Sửu hết, hội Dần bất đầu, muôn vật sinh ra. Sách Lịch nói: “Khí trời bay xuống, khí đất bốc lên trời đất giao hòa, muôn vật sinh ra”. Đến đây trời, đất sáng sủa, âm dương giao hòa, Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Dần, sinh người, sinh thú, sinh chim, gọi là tam tài, gồm trời, đất, người định vị. Cho nên nói rằng: người sinh ra ở Dần."
    src = "蓋聞天地之數,有十二萬九千六百歲為一元。\n將一元分為十二會,乃子、丑、寅 、卯、辰、巳、午、未、申、酉、戌、亥之十二支也。\n每會該一萬八百歲。\n且就 一日而論:子時得陽氣,而丑則雞鳴;\n寅不通光,而卯則日出;\n辰時食後,而巳 則挨排;\n日午天中,而未則西蹉;\n申時晡,而日落酉,戌黃昏,而人定亥。\n譬於 大數,若到戌會之終,則天地昏曚而萬物否矣。\n再去五千四百歲,交亥會之初, 則當黑暗,而兩間人物俱無矣,故曰混沌。\n又五千四百歲,亥會將終,貞下起元 ,近子之會,而復逐漸開明。"
    tgt = "Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên.\nMột nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi. \nMỗi một hội là mười nghìn tám trăm năm. \nLại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy. \nGiờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc. \nGiờ Thìn ăn cơm xong, thì giờ Tỵ đã liền kề. \nGiờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây. \nGiờ Thân là lúc mặt trời lặn ở phương tây. \nGiờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ. \nSo trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ. \nVào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn. \nTrải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết. \nHết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ. "
    align_chapters(src, tgt)