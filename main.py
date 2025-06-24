
from config import GeneratorConfig
from parallel_corpus_generator import ParallelCorpusGenerator


def main() -> None:
    config = GeneratorConfig()
    generator = ParallelCorpusGenerator(config)
    
    sect_ids = [1]
    generator.align_sections(sect_ids=sect_ids)

if __name__=="__main__":
    main()

