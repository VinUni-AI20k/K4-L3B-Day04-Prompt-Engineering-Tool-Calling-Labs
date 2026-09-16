# Hướng Dẫn Sử Dụng Web UI — IT Helpdesk AI Agent

## 🌟 Giới Thiệu Giao Diện Web Chat
Giao diện Web Chat được xây dựng đáp ứng đầy đủ tiêu chuẩn đánh giá của **Rubric Day04 (mục UI và transcript — 10 điểm)**:
- **Tool Call**: Thẻ card trực quan với icon và tên từng công cụ (`inspect_device`, `create_ticket`, `check_service_status`, `clarify`, v.v.).
- **Input Arguments**: Định dạng JSON chi tiết các tham số truyền vào công cụ (`asset_id`, `check`, `summary`, `priority`, v.v.).
- **Kết Quả / Lỗi (Results & Errors)**:
  - Hiển thị kết quả thực thi công cụ trả về.
  - Cảnh báo lỗi nổi bật (`restricted_sensitive_data`, `needs_confirmation`, `invalid_asset_id`, lỗi provider) bằng màu sắc tương phản cao (Đỏ/Cam). Không che giấu lỗi!
  - Tương tác bổ sung thông tin: Khi agent gọi `clarify`, giao diện hiển thị các nút lựa chọn trực tiếp (Yes/No hoặc danh sách lựa chọn).
- **Phiên Bản (Artifact Versioning)**:
  - Hiển thị thanh chuyển đổi nhanh các phiên bản: `v0`, `v1`, `v2`, `v3`.
  - Hiển thị mã băm đầy đủ `artifact_version` (ví dụ `v0+p7ce503377488+t0000f66b3807`).
  - Hiển thị mã băm SHA256 của `system_prompt.md` và `tools.yaml`.
- **Transcripts & Test Cases**:
  - Lưu và tải transcript trực tiếp theo định dạng chuẩn của `chat.py`.
  - Nạp các file transcript mẫu có sẵn (như `example_helpdesk.transcript.json`).
  - Danh sách test cases (Base 30 câu + Safety 12 câu) cho phép kiểm thử 1-click.

---

## 🚀 Cách Khởi Chạy Web UI

### Cách 1: Chạy trực tiếp từ thư mục `starter_v0`
```powershell
cd starter_v0
python ui.py --port 8000
```

Sau đó mở trình duyệt tại: **`http://localhost:8000`** (hoặc `http://127.0.0.1:8000`).

### Cách 2: Chạy từ thư mục gốc của Repo
```powershell
python starter_v0/ui.py --port 8000
```

---

## 🧪 Các Chế Độ Hoạt Động Của UI

1. **Chế độ Simulator (Khuyến nghị khi test offline hoặc demo nhanh)**:
   - Tự động kích hoạt khi chưa điền API key vào `.env`, hoặc khi chọn `Simulator (Offline/Demo)` trong ô Provider.
   - Mô phỏng chính xác hành vi gọi tool, truyền tham số, kiểm tra quyền và phát hiện dữ liệu nhạy cảm.

2. **Chế độ Live Provider (OpenRouter / OpenAI / Gemini / Anthropic)**:
   - Khi đã điền key vào `.env`, chọn provider tương ứng ở góc trên bên phải giao diện để kết nối trực tiếp với LLM.
