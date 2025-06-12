# Vietnamese OCR Text Cleaner - Folder Processing Edition

## Tính năng chính

- 📁 **Xử lý hàng loạt thư mục**: Xử lý tất cả file trong folder
- 🔄 **Xử lý đệ quy**: Hỗ trợ thư mục con với flag `--recursive`
- 📄 **Đa định dạng file**: Tùy chỉnh phần mở rộng file (`.txt`, `.md`, v.v.)
- 🧹 **Làm sạch nhiễu**: Loại bỏ ký tự lạ, chuẩn hóa khoảng trắng
- 📚 **Lọc từ dựa trên từ điển tiếng Việt** (QuocNgu_SinoNom_Dic.json)
- ⚙️ **Cấu hình lọc bằng file JSON**
- 📊 **Báo cáo tổng hợp chi tiết**: Thống kê đầy đủ với biểu đồ

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8
- pip package manager
- underthesea==6.8.4
- underthesea_core==1.0.4

### Cài đặt dependencies

```bash
# Cài đặt tất cả dependencies
pip install -r requirements.txt

# Để sử dụng biểu đồ thống kê
pip install matplotlib
```

### Cấu trúc dự án

```
post-ocr-normalizer/
├── main.py                      # CLI entry point (Folder processing)
├── text_cleaner.py             # Core cleaning logic
├── file_processor.py           # File & Folder I/O operations
├── statistics.py               # Statistics & Visualization
├── vietnamese_dictionary.py    # Dictionary management
├── noise_pattern_manager.py    # Noise pattern handling
├── text_tokenizer.py          # Text tokenization
├── punctuation_normalizer.py  # Punctuation normalization
├── cleaning_config.py         # Configuration classes
├── exceptions.py              # Custom exceptions
├── config_noise.json         # Noise patterns config
├── QuocNgu_SinoNom_Dic.json  # Vietnamese dictionary
└── requirements.txt           # Dependencies
```

## Cấu hình

### File config_noise.json

File cấu hình chứa các pattern regex để loại bỏ nhiễu và chuẩn hóa dấu câu:

```json
[
  { "pattern": "\\|", "replacement": "" },
  { "pattern": "\\(!\\)", "replacement": "!" },
  { "pattern": "\\(\\?\\)", "replacement": "?" },
  { "pattern": "\\(\\.\\)", "replacement": "." },
  { "pattern": "\\(\\,\\)", "replacement": "," },
  { "pattern": "\\(\\:\\)", "replacement": ":" },
  { "pattern": "\\!\\.", "replacement": "!" },
  { "pattern": "\\?\\.", "replacement": "?" },
  { "pattern": "\\,\\.", "replacement": "," },
  { "pattern": "\\:\\.", "replacement": ":" }
]
```

#### Giải thích các pattern:

- `"\\|"` → `""`: Loại bỏ ký tự pipe (|)
- `"\\(!\\)"` → `"!"`: Chuyển (!!) thành !
- `"\\(\\?\\)"` → `"?"`: Chuyển (??) thành ?
- `"\\(\\.\\)"` → `"."`: Chuyển (.) thành .
- `"\\(\\,\\)"` → `","`: Chuyển (,) thành ,
- `"\\(\\:\\)"` → `":"`: Chuyển (:\) thành :
- `"\\!\\."`→ `"!"`: Loại bỏ dấu chấm sau dấu chấm than
- `"\\?\\."` → `"?"`: Loại bỏ dấu chấm sau dấu hỏi
- `"\\,\\."` → `","`: Loại bỏ dấu chấm sau dấu phẩy
- `"\\:\\."` → `":"`: Loại bỏ dấu chấm sau dấu hai chấm

#### Thêm pattern mới:

```json
{ "pattern": "regex_pattern_ở_đây", "replacement": "chuỗi_thay_thế" }
```

### File từ điển QuocNgu_SinoNom_Dic.json (được tạo từ file QuocNgu_SinoNom_Dic.xlsx)

File từ điển chứa mapping giữa chữ Quốc ngữ và chữ Sino-Nom:

```json
[
  {
    "QuocNgu": "a",
    "SinoNom": "丫"
  },
  {
    "QuocNgu": "a",
    "SinoNom": "也"
  },
  {
    "QuocNgu": "ăn",
    "SinoNom": "𩙿"
  },
  {
    "QuocNgu": "bà",
    "SinoNom": "婆"
  }
]
```

#### Cấu trúc:

- **Array of objects**: Mỗi entry là một object
- **QuocNgu**: Từ tiếng Việt hiện đại
- **SinoNom**: Chữ Hán-Nôm tương ứng

### Cấu hình trong code

```python
from cleaning_config import CleaningConfig

config = CleaningConfig(
    min_word_length=1,          # Độ dài từ tối thiểu
    max_word_length=50,         # Độ dài từ tối đa
    preserve_punctuation=True,  # Giữ dấu câu
    case_sensitive_dictionary=False  # Không phân biệt hoa thường
)
```

## Hướng dẫn sử dụng

### Sử dụng cơ bản - Xử lý thư mục

```bash
# Xử lý tất cả file .txt trong thư mục
python main.py input_folder output_folder

# Xử lý đệ quy tất cả thư mục con
python main.py input_folder output_folder --recursive

# Xử lý nhiều loại file
python main.py input_folder output_folder --extensions .txt .md .rtf
```

### Sử dụng với cấu hình đầy đủ

```bash
python main.py input_folder output_folder \
    --recursive \
    --extensions .txt .md \
    -c config_noise.json \
    -d QuocNgu_SinoNom_Dic.json \
    --verbose
```

### Các tham số dòng lệnh

| Tham số            | Mô tả                                        | Bắt buộc |
| ------------------ | -------------------------------------------- | -------- |
| `input_folder`     | Thư mục chứa file văn bản đầu vào            | ✅       |
| `output_folder`    | Thư mục kết quả đầu ra                       | ✅       |
| `--extensions`     | Phần mở rộng file cần xử lý (mặc định: .txt) | ❌       |
| `-r, --recursive`  | Xử lý đệ quy thư mục con                     | ❌       |
| `-c, --config`     | File cấu hình noise patterns                 | ❌       |
| `-d, --dictionary` | File từ điển tiếng Việt                      | ❌       |
| `-e, --encoding`   | Encoding file (mặc định: utf-8)              | ❌       |
| `-v, --verbose`    | Hiển thị báo cáo chi tiết và biểu đồ         | ❌       |

### Ví dụ thực tế

```bash
# Xử lý thư mục sách với đầy đủ tính năng
python main.py documents/ cleaned_documents/ \
    --recursive \
    --extensions .txt .md \
    -c config_noise.json \
    -d QuocNgu_SinoNom_Dic.json \
    --verbose

# Xử lý nhanh thư mục đơn giản
python main.py input_texts/ output_texts/ --verbose

# Xử lý file Excel, Word documents (cần convert trước)
python main.py raw_ocr_texts/ cleaned_texts/ \
    --extensions .txt \
    -c config_noise.json \
    -d QuocNgu_SinoNom_Dic.json
```

## Quy trình xử lý

### Pipeline xử lý thư mục

```
1. Khám phá file
   ↓ Tìm tất cả file theo extension và recursive setting

2. Tạo cấu trúc thư mục đầu ra
   ↓ Giữ nguyên cấu trúc thư mục gốc

3. Xử lý từng file
   ↓ Áp dụng pipeline làm sạch văn bản

4. Thu thập thống kê
   ↓ Tổng hợp kết quả từ tất cả file

5. Tạo báo cáo tổng hợp
   ↓ Hiển thị thống kê và biểu đồ
```

### Pipeline 9 bước làm sạch văn bản (cho từng file) - Tối ưu hóa

```
1. Đọc file đầu vào
   ↓ Kiểm tra encoding, format

2. Loại bỏ noise
   ↓ Áp dụng regex patterns từ config

3. Chuẩn hóa khoảng trắng
   ↓ Xóa space/tab/newline thừa

4. Tokenization (Lần 1)
   ↓ Tách từ thông minh (underthesea hoặc simple)

5. Lọc tokens hợp lệ (Lần 1)
   ↓ Kiểm tra length, pattern ký tự

6. Xử lý underscore (Tự động)
   ↓ Thay "_" bằng " " trong tất cả tokens

7. Ghép nối và chuẩn hóa dấu câu
   ↓ Xử lý spacing xung quanh dấu câu

8. Lọc từ điển
   ↓ Giữ từ có trong từ điển VN

9. Tokenization và lọc (Lần 2)
   ↓ Tách từ và lọc tokens lần cuối

10. Ghi file kết quả
    ↓ Xuất văn bản đã làm sạch + thống kê
```

### Thống kê được tính toán

- **Ký tự**: Original → Cleaned (% reduction)
- **Từ**: Tổng số từ và tỷ lệ giảm
- **Câu**: Số câu và sự thay đổi
- **Chars/sentence**: Chiều dài trung bình câu
- **Words/sentence**: Mật độ từ trên câu

## Sử dụng trong code Python

### Xử lý thư mục

```python
from pathlib import Path
from text_cleaner import TextCleaner
from file_processor import FileProcessor
from statistics import StatisticsReporter

# Khởi tạo
cleaner = TextCleaner(
    config_path=Path("config_noise.json"),
    dictionary_path=Path("QuocNgu_SinoNom_Dic.json"),
    verbose=True
)
processor = FileProcessor()
reporter = StatisticsReporter()

# Xử lý thư mục
file_stats, total_original, total_cleaned, failed_files = processor.process_folder(
    input_folder=Path("documents/"),
    output_folder=Path("cleaned/"),
    cleaner=cleaner,
    extensions=['.txt', '.md'],
    recursive=True,
    verbose=True
)

# Tạo báo cáo
reporter.generate_report(file_stats, total_original, total_cleaned,
                        Path("cleaned/"), failed_files, Path("documents/"))

# Hiển thị biểu đồ chi tiết
reporter.generate_detailed_report(file_stats, total_original, total_cleaned)
```

### Xử lý file đơn lẻ

```python
# Xử lý file đơn
original_len, cleaned_len, stats = processor.process_file(
    Path("input.txt"),
    Path("output.txt"),
    cleaner
)

# Xử lý text trực tiếp
cleaned_text = cleaner.clean_text("Văn bản cần làm sạch...")
statistics = cleaner.get_cleaning_stats()

print(f"Processed: {original_len} → {cleaned_len} characters")
print(f"Stats: {statistics}")
```

## Cấu trúc thư mục đầu ra

Hệ thống tự động giữ nguyên cấu trúc thư mục:

```
Input:                          Output:
documents/                      cleaned_documents/
├── chapter1/                   ├── chapter1/
│   ├── intro.txt              │   ├── intro.txt
│   └── content.txt            │   └── content.txt
├── chapter2/                  ├── chapter2/
│   └── story.txt              │   └── story.txt
└── appendix.txt               └── appendix.txt
```

## Troubleshooting

### Lỗi thường gặp

**Q: Matplotlib không hiển thị biểu đồ**

```bash
pip install matplotlib
```

**Q: Lỗi encoding file**

```bash
python main.py input_folder output_folder -e utf-8-sig
```

**Q: Không tìm thấy file trong thư mục**

```bash
# Kiểm tra phần mở rộng file
python main.py input_folder output_folder --extensions .txt .md --verbose

# Sử dụng recursive để tìm trong thư mục con
python main.py input_folder output_folder --recursive
```

**Q: Từ điển không load**

```bash
# Kiểm tra format JSON
python -c "import json; json.load(open('QuocNgu_SinoNom_Dic.json'))"
```

**Q: Thư mục đầu ra không tạo được**

```bash
# Kiểm tra quyền ghi
mkdir -p output_folder
python main.py input_folder output_folder
```

### Exit codes

- `0`: Thành công
- `1`: Lỗi cấu hình/input
- `2`: Lỗi xử lý file
- `3`: Lỗi hệ thống

### Tối ưu hiệu suất

- **File nhỏ (<1MB)**: Xử lý nhanh, không cần tối ưu
- **File lớn (>10MB)**: Sử dụng `--verbose` để theo dõi tiến trình
- **Nhiều file**: Tổ chức thư mục hợp lý, sử dụng `--recursive`
- **Lỗi memory**: Xử lý từng thư mục con riêng biệt
