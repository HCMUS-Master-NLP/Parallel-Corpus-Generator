

import pandas as pd
from pathlib import Path
import re
from tqdm import tqdm
import os

from config import GeneratorConfig
from preprocessor import QuocNguPreprocessor, SinoNomPreprocessor
from bertalign.eval import *
from bertalign import Bertalign


def save_txt(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as fp:
        fp.writelines(text)


def create_eval_data_from_excel(excel_path: Path, output_folder: Path) -> None:
    chi_output_folder = output_folder / "chi"
    vie_output_folder = output_folder / "vie"
    gold_output_folder = output_folder / "gold"
    
    chi_output_folder.mkdir(parents=True, exist_ok=True)
    vie_output_folder.mkdir(parents=True, exist_ok=True)
    gold_output_folder.mkdir(parents=True, exist_ok=True)
    
    df_excel = pd.read_excel(excel_path, header=None)
    start = df_excel.index.start 
    end = df_excel.index.stop
    
    para_id = None
    chi_sent_id = 0
    vie_sent_id = 0
    
    chi_para_dict = {}
    vie_para_dict = {}
    aligned_id_dict = {}
    
    config = GeneratorConfig()
    quocngu_preprocessor = QuocNguPreprocessor(config.noise_json_path)
    sinonom_preprocessor = SinoNomPreprocessor(config)
    
    for i in tqdm(range(start, end),desc="Đang tạo dữ liệu eval từ golden data"):
        lines = str(df_excel.iloc[i]).strip().split('\n')
        chinese_sents = lines[0][1:].strip()
        vietnamese_sents = lines[1][1:-2].strip()
        
        match_0 = re.search(r"Paragraph (\d+)",chinese_sents)
        match_1 = re.search(r"\\n",chinese_sents)
        
        if match_0:
            para_id = str(match_0.group(1))

            chi_para_dict[str(para_id)] = []
            vie_para_dict[str(para_id)] = []
            aligned_id_dict[str(para_id)] = []
            
            chi_sent_id = 0
            vie_sent_id = 0
            
        elif not match_1:
            chinese_sent_list = sinonom_preprocessor.split_sents(chinese_sents.strip())
            vietnamese_sent_list = quocngu_preprocessor.split_sents(vietnamese_sents.strip())
            
            chi_id_list = []
            vie_id_list = []
            
            for sent in chinese_sent_list:
                chi_para_dict[str(para_id)].append(sent)
                chi_id_list.append(chi_sent_id)
                chi_sent_id += 1
                
            for sent in vietnamese_sent_list:
                vie_para_dict[str(para_id)].append(sent)
                vie_id_list.append(vie_sent_id)
                vie_sent_id += 1
            
            aligned_id_dict[str(para_id)].append(f"{chi_id_list}:{vie_id_list}")
            
    
    for i in aligned_id_dict.keys():
        aligned_ids = "\n".join(aligned_id_dict[i])
        chi_para = "\n".join(chi_para_dict[i])
        vie_para = "\n".join(vie_para_dict[i])
        
        chi_path = chi_output_folder / f"{int(i):03}.txt"
        vie_path = vie_output_folder / f"{int(i):03}.txt"
        gold_path = gold_output_folder / f"{int(i):03}.txt"
        
        save_txt(aligned_ids,gold_path)
        save_txt(chi_para,chi_path)
        save_txt(vie_para,vie_path)
            
    
def main() -> None:
    excel_path = Path("./data/Golden_CnVn_alignment/tqdn1_ch_vn.xlsx")
    output_folder = Path("./data/eval")
    
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    create_eval_data_from_excel(excel_path, output_folder)
    
    src_dir = output_folder / "chi"
    tgt_dir = output_folder / "vie"
    gold_dir = output_folder / "gold"
    
    test_alignments = []
    gold_alignments = []
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file).replace("\\","/")
        tgt_file = os.path.join(tgt_dir, file).replace("\\","/")
        src = open(src_file, 'rt', encoding='utf-8').read()
        tgt = open(tgt_file, 'rt', encoding='utf-8').read()

        print("Start aligning {} to {}".format(src_file, tgt_file))
        aligner = Bertalign(src, tgt, is_split=True)
        aligner.align_sents()
        test_alignments.append(aligner.result)

        gold_file = os.path.join(gold_dir, file)
        gold_alignments.append(read_alignments(gold_file))
    
    scores = score_multiple(gold_list=gold_alignments, test_list=test_alignments)
    log_final_scores(scores)

    
if __name__=="__main__":
    main()