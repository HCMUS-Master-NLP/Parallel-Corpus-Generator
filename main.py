
import sys

from config import GeneratorConfig
from parallel_corpus_generator import ParallelCorpusGenerator

def main():
    start_sect = int(sys.argv[1])
    end_sect = int(sys.argv[2])
    
    config = GeneratorConfig()
    generator = ParallelCorpusGenerator(config)

    sect_ids = [i for i in range(start_sect,end_sect+1)]
    generator.align_and_save_sections(sect_ids=sect_ids)

if __name__ == "__main__":
    main()