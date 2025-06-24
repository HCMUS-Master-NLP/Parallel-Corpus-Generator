import logging
import re
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class XMLBuilder:
    def __init__(
        self,
        file: str,
        title: str,
        volume: str,
        author: str,
        period: str,
        language: str,
        source: str,
    ):
        """Meta data sample:
        meta_data = {
            "file": "TDK_001",
            "title": "Tây Du Ký",
            "volume": "1",
            "author": "Ngô Thừa Ân",
            "period": "",
            "lang": "Việt",
            "source": "",
            "page_id" : [],
        }

        Args:
            file (str): File id
            title (str): Document title
            volume (str): Document Volume
            author (str): Document Author
            period (str): Document period
            language (str): Document languge
            source (str): Document source
        """

        self.file_id = file
        self.title = title
        self.root = ET.Element("root")
        self.file = ET.SubElement(self.root, "FILE", ID=self.file_id)

        # Metadata
        meta = ET.SubElement(self.file, "meta")
        ET.SubElement(meta, "TITLE").text = title
        ET.SubElement(meta, "VOLUME").text = volume
        ET.SubElement(meta, "AUTHOR").text = author
        ET.SubElement(meta, "PERIOD").text = period
        ET.SubElement(meta, "LANGUAGE").text = language
        ET.SubElement(meta, "SOURCE").text = source

        self.spit_sencetenc_func = self._split_sentence
        self.xlm_content = None
        self.pages = []

    def set_pages(self, pages: List):
        """Set list of pages for texts in one section
        Args:
            pages (List): List of pages in one section
        """
        self.pages = pages

    def _split_sentence(self, text: str) -> List:
        """Default spliting sentence function
        Split sentences by '.', '!', '?' (basic rule-based segmentation)
        Args:
            text (str): _description_

        Returns:
            List: _description_
        """
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
        return sentences

    def add_section_with_text(self, sect_id: str, sect_name: str, texts: List):
        """
        Add a section (SECT) with parsed sentences in STC tags from input text.

        Args:
            sect_id (str): Section ID like "TDK_001.001"
            sect_name (str): Name of the section
            text (str): Raw input text to split into sentences and convert to STC tags
        """
        sect = ET.SubElement(self.file, "SECT", ID=sect_id, NAME=sect_name)
        for text, page_num in zip(texts, self.pages):
            page_id = f"{sect_id}.{int(page_num):03}"
            page = ET.SubElement(sect, "PAGE", ID=page_id)
            sentences = self._split_sentence(text)
            for i, sentence in enumerate(sentences, start=1):
                stc_id = f"{page_id}.{i:02}"
                stc = ET.SubElement(page, "STC", ID=stc_id)
                stc.text = sentence

    def to_string(self) -> str:
        """Return pretty-printed XML string."""
        xml_str = ET.tostring(self.root, encoding="unicode")
        return minidom.parseString(xml_str).toprettyxml(indent="    ")

    def save(
        self,
        output_name: str = None,
        output_dir: Path = Path("."),
        encoding: str = "utf-8",
    ):
        """
        Saves the XML string to a file with .xml extension.

        Args:
            xml_string (str): The XML content as a string.
            output_name (str): Base name for the output file (default is "output").
        """

        if not output_name:
            output_name = f"{self.title}.xml"

        # Create parent directories if needed
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        full_path = output_dir / output_name
        with full_path.open("w", encoding=encoding) as f:
            f.write(self.to_string())
        logger.info(f"Save file to {full_path}")

    def save_by_section(
        self,
        output_name: str = None,
        output_dir: Path = Path("."),
        encoding: str = "utf-8",
    ):
        """
        Saves the XML content by section to separate files.

        Args:
            output_name (str): Base name for the output file (default is None).
            output_dir (Path): Directory to save the files (default is current directory).
            encoding (str): Encoding for the output files (default is "utf-8").
        """
        if not output_name:
            output_name = self.title

        # extract data from the root element
        meta_elem = self.root.find("FILE/meta")

        for sect in self.root.findall("FILE/SECT"):

            sect_id = sect.get("ID")
            sect_name = sect.get("NAME")
            file_name = f"{output_name}_{sect_id}.xml"
            full_path = output_dir / file_name

            # Build new XML structure
            new_root = ET.Element("root")
            file = ET.SubElement(new_root, "FILE", ID=self.file_id)
            new_root.append(deepcopy(file))
            if meta_elem is not None:
                new_root.find("FILE").append(deepcopy(meta_elem))
            new_root.find("FILE").append(deepcopy(sect))

            with full_path.open("w", encoding=encoding) as f:
                xml_str = ET.tostring(new_root, encoding="unicode")
                xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
                f.write(xml_str)
            logger.info(f"Save section {sect_name} to {full_path}")


def main():

    file = "TDK_001"
    builder = XMLBuilder(
        file=file,
        title="Tây Du Ký",
        volume="1",
        author="Ngô Thừa Ân",
        period="",
        language="Việt",
        source="",
    )
    dummy_data = [
        {
            "section_value": 1,
            "section_content": {
                "text": [
                    """HỒI THỨ NHẤT
                    Gốc thiêng ấp ủ, nguồn rộng chảy
                    Tâm tính sửa sang, đạo lớn sinh
                    Có bài thơ rằng:
                    Thuở hoang sơ đất trời chưa tỏ.
                    Chốn mênh mông nào có bóng người.
                    Từ khi Bàn Cổ ra đời.
                    Đục trong phân biệt, khác thời hỗn mang.
                    Che chở khắp nhờ ơn trời đất.
                    Phát minh ra muôn vật tốt thay.
                    Muốn hay tạo hóa công dày, “Tây du”[10] truyện ấy đọc ngay đi nào.
                    Từng nghe số của trời đất, gồm một trăm hai mươi chín nghìn sáu trăm năm là một nguyên. Một nguyên chia làm mười hai hội, tức mười hai chi: Tý, Sửu,Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi. Mỗi một hội là mười nghìn tám trăm năm. Lại lấy một ngày mà nói: giờ Tý được khí dương, thì giờ Sửu gà gáy. Giờ Dần ánh sáng chưa khắp, thì giờ Mão mặt trời mọc. Giờ Thìn ăn cơm xong, thì giờ Tỵ""",
                    """
                    đã liền kề. Giờ Ngọ mặt trời ở giữa trời, thì giờ Mùi ngả về tây. Giờ Thân là lúc mặt trời lặn ở phương tây. Giờ Tuất là lúc hoàng hôn và giờ Hợi mọi người yên nghỉ. So trong số lớn, đến cuối hội Tuất là lúc trời đất tối tăm mờ mịt, muôn vật ở vào vận bĩ. Vào đầu hội Hợi, đúng lúc đang mờ mịt, người và vật đều chưa có, nên gọi là hỗn độn. Trải qua bốn nghìn năm trăm năm nữa, hội Hợi sắp hết. Hết vòng lại quay lại từ đầu, chuyển sang hội Tý, trở lại dần dần sáng tỏ. Thiệu Khang Tiết[11] nói:
                    “Giữa giờ Tý đông chí,
                    Lòng trời chẳng đổi dời
                    Lúc một dương lay động
                    Vạn vật chưa ra đời”
                    Đến đây, trời bắt đầu có rễ. Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Tý, những thứ nhẹ trong bay lên, có mặt trời, mặt trăng, tinh tú. Mặt trời, mặt trăng tinh tú (tinh và thần) gọi là tứ tượng. Cho nên nói rằng: trời mở ở Tý. Lại trải qua năm nghìn bốn trăm năm, hội Tý sắp hết, gần sang hội Sửu, thì dần dần rắn chắc. Kinh dịch nói: “Lớn thay đức nguyên của quẻ Càn! Tuyệt thay đức nguyên của kẻ khôn! Vạn vật nhờ đó sinh ra, là thuận theo trời”. Đến đây đất bắt đầu ngưng kết. Lại trải qua bốn nghìn năm
                    """,
                ],
                "page_num": ["47", "48"],
            },
        },
        {
            "section_value": 2,
            "section_content": {
                "text": [
                    """trăm năm, đúng vào hội Sửu, những thứ nặng đục ngưng xuống. Có nước, có lửa, có núi, có đá, có đất. Nước, lửa, núi, đá, đất gọi là ngũ hình. Cho nên nói rằng: Đất mở ở Sửu. Lại trải qua năm nghìn bốn trăm năm, hội Sửu hết, hội Dần bất đầu, muôn vật sinh ra.Sách Lịch nói: “Khí trời bay xuống, khí đất bốc lên trời đất giao hòa, muôn vật sinh ra”. Đến đây trời, đất sáng sủa, âm dương giao hòa, Lại trải qua năm nghìn bốn trăm năm, đúng vào hội Dần, sinh người, sinh thú, sinh chim, gọi là tam tài, gồm trời, đất, người định vị. Cho nên nói rằng: người sinh ra ở Dần. Nhớ xưa từ thuở Bàn Cổ mới mở mang, đời Tam Hoàng vừa cai trị, đời Ngũ đế định ra nhân luân, bấy giờ thế giới mới chia ra làm bốn châu lớn.
                1. Đông Thắng Thần Châu.
                2. Tây Ngưu Hạ Châu.
                3. Nam Thiệm Bộ Châu.
                4. Bắc Câu Lư Châu.
                Bộ sách này chỉ nói riêng về Đông Thắng Thần Châu. Lúc đó ngoài biển mới thấy có một nước. Nước này gọi là nước Ngạo Lai ở sát gần biển lớn. Giữa biển có một ngọn núi đẹp, gọi là núi Hoa Quả. Chính núi này là mạch tổ của mười châu, cội nguồn của ba""",
                ],
                "page_num": ["49"],
            },
        },
    ]

    # Replace with actual split sentence for Chinese and Vietnamese text
    # builder.spit_sencetenc_func = ...
    for data in dummy_data:
        texts = data["section_content"]["text"]
        sect_value = data["section_value"]
        page_num = data["section_content"]["page_num"]
        builder.set_pages(page_num)
        sect_id = f"{file}.{sect_value:03d}"
        builder.add_section_with_text(
            sect_id=sect_id, sect_name="Tây Du Ký", texts=texts
        )

    builder.save_by_section()
    builder.save()


if __name__ == "__main__":
    main()
