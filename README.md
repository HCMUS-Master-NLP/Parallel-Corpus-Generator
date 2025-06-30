# HCMUS K34 NLP - MIDTERM PROJECT

##  Yêu cầu hệ thống

- python 3.11
- pip 

## Cài đặt thư viện cần thiết

```bash
pip install -r requirements.txt
```

## Hướng dẫn sử dụng
### 1. Dóng hàng theo câu trong mỗi chương của tác phẩm.
```bash
# Tạo kết quả dóng hàng theo câu từ start_sect_id đến end_sect_id
# Để trống các id thì mặc định từ hồi 1 đến hồi 100
python align_sections.py <start_sect_id> <end_sect_id>
```

### 2. Thống kê kết quả dóng hàng theo câu của những hồi/chương đã được dóng.
```bash
python statistics.py
```

### 3. Tạo một tệp XML dóng hàng theo câu duy nhất từ bước 1.
```bash
python merge_aligned_sections.py
```

### 4. Ngoài ra, có thể đánh giá mô hình Bertalign trên tập Golden_CnVn_alignment.
```bash
python eval_model.py
```