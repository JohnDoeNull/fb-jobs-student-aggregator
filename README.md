# FB Jobs Student Aggregator

Dự án thu thập và tổng hợp tin tuyển dụng từ các group Facebook, tập trung cho:
- Sinh viên / thực tập
- Việc thời vụ / part-time
- Việc IT

## Mục tiêu
- Cào dữ liệu bài đăng việc làm từ nhiều group FB.
- Chuẩn hoá dữ liệu (tiêu đề, mô tả, địa điểm, mức lương, loại việc).
- Phân loại theo nhãn: `student`, `intern`, `part-time`, `it`, `other`.
- Xuất feed tổng hợp để tra cứu nhanh (CSV/JSON/API).

## Cấu trúc ban đầu
- `src/collectors/`: module crawler
- `src/pipeline/`: làm sạch + chuẩn hoá + phân loại
- `data/raw/`: dữ liệu thô
- `data/processed/`: dữ liệu đã xử lý
- `configs/groups.example.yaml`: danh sách group nguồn mẫu

## Lưu ý pháp lý
- Tuân thủ Terms of Service của nền tảng.
- Chỉ thu thập dữ liệu công khai/được cấp quyền.
- Không lưu thông tin nhạy cảm không cần thiết.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
PYTHONPATH=. python -m src.main --config configs/groups.yaml
uvicorn src.api:app --reload
```

## Phase 2: Live crawler (Playwright)
- Cấu hình group tại `configs/groups.yaml`
- Export cookies Facebook dạng JSON vào: `data/secrets/facebook_cookies.json`
- Chạy pipeline:
```bash
bash scripts/run_pipeline.sh
```
- Refresh qua API:
```bash
curl -X POST 'http://127.0.0.1:8000/refresh'
```

> Nếu thiếu cookies hoặc crawl lỗi, hệ thống tự fallback qua mock collector để service không downtime.
