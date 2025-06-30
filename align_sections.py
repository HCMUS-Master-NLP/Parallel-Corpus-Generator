
import sys
from config import GeneratorConfig
from parallel_corpus_generator import ParallelCorpusGenerator

def main():
    arg_1 = sys.argv[1]
    arg_2 = sys.argv[2]
    
    if not arg_1 and not arg_2:
        start_sect = int(arg_1)
        end_sect = int(arg_2)
    else:
        start_sect = 1
        end_sect = 100
    
    config = GeneratorConfig()
    generator = ParallelCorpusGenerator(config)

    remove_sect_ids = [4,5,35]
    sect_ids = [i for i in range(start_sect,end_sect+1) if i not in remove_sect_ids]
    generator.align_and_save_sections(sect_ids=sect_ids)

if __name__ == "__main__":
    main()