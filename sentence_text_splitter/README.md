# Vietnamese Text Sentence Splitter

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)

## Installation

Simply download the `main.py` file or clone this repository:

```bash
git clone <repository-url>
cd split-sentence
```

## Usage

### Basic Usage

```bash
python main.py input_folder output_folder
```

### Command Line Options

```bash
python main.py [-h] [--json] [--threads THREADS] input_folder output_folder
```

**Arguments:**

- `input_folder`: Path to the input folder containing Vietnamese text files (.txt, .text)
- `output_folder`: Path to the output folder where processed files will be saved

**Options:**

- `--json`: Output sentences in JSON format as a list (default: plain text, one sentence per line)
- `--threads THREADS`: Number of threads to use for processing
- `-h, --help`: Show help message and exit

### Examples

#### Basic sentence splitting (processes all .txt and .text files in the folder):

```bash
python main.py vietnamese_texts output_sentences
```

#### Output in JSON format:

```bash
python main.py vietnamese_texts output_sentences --json
```

#### Use specific number of threads:

```bash
python main.py vietnamese_texts output_sentences --threads 4
```

## Input/Output Formats

### Input

- Folder containing plain text files (UTF-8 encoded)
- Supported file extensions: `.txt`, `.text`
- Vietnamese text with standard punctuation

### Output Options

**Text Format (default):**

- Creates `.txt` files in the output folder
- Each file contains sentences from the corresponding input file, one per line

**JSON Format (--json flag):**

- Creates `.json` files in the output folder
- Each file contains an array of sentences from the corresponding input file

```json
["Sentence 1 here.", "Sentence 2 here.", "Sentence 3 here."]
```

## How It Works

1. **Folder Scanning**: Automatically finds all text files (.txt, .text) in the input folder
2. **Text Preprocessing**: Normalizes whitespace and cleans the input text for each file
3. **Smart Chunking**: Divides large texts into chunks at sentence boundaries for parallel processing
4. **Parallel Processing**: Processes multiple chunks simultaneously using ThreadPoolExecutor
5. **Sentence Detection**: Uses regex patterns to identify Vietnamese sentence endings (`.`, `!`, `?`, `…`)
6. **Post-processing**: Filters out very short fragments and combines results
7. **Output Generation**: Creates corresponding output files in the specified output folder

## Performance

- **Batch Processing**: Processes multiple files in a single run
- **Automatic Scaling**: Automatically detects CPU cores and optimizes thread count
- **Memory Efficient**: Processes text in chunks to handle large files
- **Fast Processing**: Parallel processing significantly reduces processing time for large texts

## Technical Details

### Supported File Types

The tool automatically processes files with these extensions:

- `.txt`
- `.text`

### Sentence Boundary Detection

The tool recognizes Vietnamese sentence endings using these patterns:

- Period (`.`)
- Exclamation mark (`!`)
- Question mark (`?`)
- Ellipsis (`…`)

### Output File Naming

- **Text output**: `original_filename.txt`
- **JSON output**: `original_filename.json`

## Examples with Sample Data

### Input folder structure (`input_texts/`):

```
input_texts/
├── sample1.txt
├── sample2.txt
└── document.text
```

### Sample file content (`input_texts/sample1.txt`):

```
Xin chào! Tôi tên là Minh. Hôm nay thời tiết rất đẹp. Bạn có muốn đi chơi không?
```

### Command:

```bash
python main.py input_texts output_sentences
```

### Output folder structure (`output_sentences/`):

```
output_sentences/
├── sample1.txt
├── sample2.txt
└── document.txt
```

### Output file content (`output_sentences/sample1.txt`):

```
Xin chào!
Tôi tên là Minh.
Hôm nay thời tiết rất đẹp.
Bạn có muốn đi chơi không?
```

### JSON Output Example:

```bash
python main.py input_texts output_sentences --json
```

**Output file content (`output_sentences/sample1.json`):**

```json
[
  "Xin chào!",
  "Tôi tên là Minh.",
  "Hôm nay thời tiết rất đẹp.",
  "Bạn có muốn đi chơi không?"
]
```
