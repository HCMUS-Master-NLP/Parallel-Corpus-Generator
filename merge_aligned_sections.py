

import xml.etree.ElementTree as ET
from pathlib import Path
from config import GeneratorConfig
import pandas as pd


def merge_xml_with_file_and_meta(xml_files, output_path):
    # Lấy FILE + meta từ file đầu tiên
    tree_first = ET.parse(xml_files[0])
    root_first = tree_first.getroot()

    file_elem = root_first.find("FILE")
    file_id = file_elem.get("ID")

    # Tạo <root> mới và gắn <FILE> đầu tiên vào
    merged_root = ET.Element("root")
    new_file_elem = ET.Element("FILE", ID=file_id)

    # Thêm <meta> từ file đầu tiên
    meta_elem = file_elem.find("meta")
    if meta_elem is not None:
        new_file_elem.append(meta_elem)

    # Gộp các <SECT> từ tất cả file
    for file_path in xml_files:
        tree = ET.parse(file_path)
        file_elem = tree.getroot().find("FILE")
        sects = file_elem.findall("SECT")
        for sect in sects:
            new_file_elem.append(sect)

    # Gắn FILE đã gộp vào root
    merged_root.append(new_file_elem)

    # Xuất file kết quả
    ET.ElementTree(merged_root).write(output_path, encoding="utf-8", xml_declaration=True)


def create_excel_from_xml(xml_path, excel_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    rows = []
    # Tìm tất cả các STC
    for stc in root.findall(".//STC"):
        stc_id = stc.get("ID", "")
        c_text = stc.findtext("C", "").strip()
        v_text = stc.findtext("V", "").strip()

        rows.append({
            "ID": stc_id,
            "Câu chữ Hán Nôm": c_text,
            "Câu chữ Quốc Ngữ": v_text
        })
        
    # Ghi ra Excel
    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False)


def main():
    aligned_dir = Path('./data/aligned_section_xml')
    xml_files = sorted(aligned_dir.glob("*.xml"), key=lambda f: int(f.stem))  # f.stem = '001' → int = 1

    # Save in XML
    generator_config = GeneratorConfig()
    output_file = Path(f"./data/output/{generator_config.xml_metadata['file id']}.xml")
    merge_xml_with_file_and_meta(xml_files, output_file)
    
    # Save in Excel
    excel_path = Path(f"./data/output/{generator_config.xml_metadata['file id']}.xlsx")
    create_excel_from_xml(output_file, excel_path)


if __name__=="__main__":
    main()