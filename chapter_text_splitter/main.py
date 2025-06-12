import argparse
import logging
from pathlib import Path
import sys

def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input_folder',required=True,type=str)
    parser.add_argument('-o','--output_folder',required=True,type=str)
    parser.add_argument('-l','--language',required=True,choices=["viet", "han"],default="han")
    parser.add_argument('-c','--config_json',required=True,type=str)
    return parser


def main() -> None:
    logger = logging.getLogger(__name__)
    
    parser = create_argument_parser()
    args = parser.parse_args()

    # Convert string paths to Path objects
    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder)

    # Validate input folder
    if not input_folder.exists():
        print(
            f"Error: Input folder '{input_folder}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not input_folder.is_dir():
        print(f"Error: '{input_folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    main()