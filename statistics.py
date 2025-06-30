
from pathlib import Path
import os
import json
import numpy as np
from tqdm import tqdm

def statistics_on_aligned_sections(data_dir: Path):
    aligned_dir = data_dir / "aligned_section_stat"
    
    num_pair_list = []
    num_paragraph_list = []
    paragraph_length_list = []
    sentence_dict = {'vie':{},'chi':{}}
    sentence_dict['vie']['sentence_length_list'] = []
    sentence_dict['chi']['sentence_length_list'] = []
    sentence_dict['vie']['unique_token_list'] = []
    sentence_dict['chi']['unique_token_list'] = []
    
    for file_name in tqdm(os.listdir(aligned_dir),desc='Đang thực hiện đọc các tệp aligned section stat'):
        file_path = aligned_dir / file_name
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            num_pair_list.append(data['num_pairs'])
            num_paragraph_list.append(data['num_paragraphs'])
            paragraph_length_list.append(data['paragraph_length_list'])
            sentence_dict['vie']['sentence_length_list'].append(data['vietnamese']['sentence_length_list'])
            sentence_dict['chi']['sentence_length_list'].append(data['chinese']['sentence_length_list'])
            
            sentence_dict['vie']['unique_token_list'].append([token.lower() for token in data['vietnamese']['unique_token_list']])
            sentence_dict['chi']['unique_token_list'].append(data['chinese']['unique_token_list'])
        
    stat = {}
    stat['num_pairs'] = sum(num_pair_list)
    
    stat['min_para_per_section'] = min(num_paragraph_list)
    stat['max_para_per_section'] = max(num_paragraph_list)
    stat['mean_para_per_section'] = np.mean(num_paragraph_list)
    
    stat['min_para_length'] = min([min(i) for i in paragraph_length_list])
    stat['max_para_length'] = max([max(i) for i in paragraph_length_list])
    stat['mean_para_length'] = np.mean([np.mean(i) for i in paragraph_length_list])
    
    stat['min_vie_sent_length'] = min([min(i) for i in sentence_dict['vie']['sentence_length_list']])
    stat['max_vie_sent_length'] = max([max(i) for i in sentence_dict['vie']['sentence_length_list']])
    stat['mean_vie_sent_length'] = np.mean([np.mean(i) for i in sentence_dict['vie']['sentence_length_list']])
    
    stat['min_chi_sent_length'] = min([min(i) for i in sentence_dict['chi']['sentence_length_list']])
    stat['max_chi_sent_length'] = max([max(i) for i in sentence_dict['chi']['sentence_length_list']])
    stat['mean_chi_sent_length'] = np.mean([np.mean(i) for i in sentence_dict['chi']['sentence_length_list']])
    
    vie_unique_token_list = []
    for token_list in sentence_dict['vie']['unique_token_list']:
        vie_unique_token_list.extend(token_list)
        vie_unique_token_list = list(set(vie_unique_token_list))
    
    chi_unique_token_list = []
    for token_list in sentence_dict['chi']['unique_token_list']:
        chi_unique_token_list.extend(token_list)
        chi_unique_token_list = list(set(chi_unique_token_list))
    
    stat['num_vie_unique_token'] = len(vie_unique_token_list)
    stat['num_chi_unique_token'] = len(chi_unique_token_list)
    
    stat_text = (
        f"Number of aligned sentences: {stat['num_pairs']}\n"
        f"Mean number of paragraph per section: {stat['mean_para_per_section']:.4f}\n"
        f"Min paragraph length: {stat['min_para_length']}\n"
        f"Max paragraph length: {stat['max_para_length']}\n"
        f"Mean paragraph length: {stat['mean_para_length']:.4f}\n"
        f"Min vietnamese sentence length: {stat['min_vie_sent_length']}\n"
        f"Max vietnamese sentence length: {stat['max_vie_sent_length']}\n"
        f"Mean vietnamese sentence length: {stat['mean_vie_sent_length']:.4f}\n"
        f"Min chinese sentence length: {stat['min_chi_sent_length']}\n"
        f"Max chinese sentence length: {stat['max_chi_sent_length']}\n"
        f"Mean chinese sentence length: {stat['mean_chi_sent_length']:.4f}\n"
        f"Number of unique vietnamese tokens: {stat['num_vie_unique_token']}\n"
        f"Number of unique chinese tokens: {stat['num_chi_unique_token']}\n"
    )
    
    file_path = data_dir / f"output/stat.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as file:
        file.writelines(stat_text)

def main() -> None:
    data_dir = Path("./data")
    statistics_on_aligned_sections(data_dir)

if __name__=="__main__":
    main()