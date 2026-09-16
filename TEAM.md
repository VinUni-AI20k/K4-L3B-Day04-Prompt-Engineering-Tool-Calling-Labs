# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Một cái gì đó
- Người đại diện / MSSV: Lê Đức Hùng — 2A202602849
- Tên repo: K4B-L3-DAY04-Motcaigido
- URL repo, nhánh nộp, commit chốt: [URL repo](https://github.com/Biocuatoe/K4B-L3-DAY04-Motcaigido)

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyễn Huy Hoàng | 2A202602738 | [@Hoang-H-Nguyen](https://github.com/Hoang-H-Nguyen) | **TV1 - v0 (baseline)**: Chạy v0, phân tích 3 nhóm lỗi, đề xuất giả thuyết #1 (đoán ID thay vì hỏi) | `starter_v0/`, `runs/v0_B_base_*.json` |
| Nguyễn Văn Thăng | 2A202602835 | [@nguyenthang23092005](https://github.com/nguyenthang23092005) | **TV2 - v1**: Sửa artifact theo giả thuyết #1, chạy v1, so sánh với v0, đề xuất giả thuyết #2 (tạo ticket không xác nhận) | `artifacts/system_prompt.md`, `runs/v1_B_base_*.json` |
| Lê Đức Hùng | 2A202602849 | [@Biocuatoe](https://github.com/Biocuatoe) | **TV3 - v2**: Sửa artifact theo giả thuyết #2, chạy v2, so sánh với v1, đề xuất giả thuyết #3 (sai/thiếu tham số), viết UI chat | `artifacts/system_prompt.md`, `runs/v2_B_base_*.json`, `ui/` |
| Nguyễn Hà Khuê | 2A202602938 | [@khuengha](https://github.com/khuengha) | **TV4 - v3 + tích hợp**: Sửa artifact theo giả thuyết #3, chạy v3, chạy lại toàn bộ v0→v3 để tổng hợp version_log.csv, viết report, xây webapp + UI (`webapp.py`, `webapp/`), hoàn thiện repo, chạy adversarial | `artifacts/tools.yaml`, `runs/v3_B_base_*.json`, `artifacts/REPORT.md`, `artifacts/version_log.csv`, `webapp.py`, `webapp/` |

## Nhận xét chung

- **Kết quả và bằng chứng:**
  - v0 (baseline): **20/30** (case_accuracy = 0.6667) — điểm khởi đầu
  - v1: **23/30** (case_accuracy = 0.7667) — cải thiện +3 case sau khi thêm quy tắc "hỏi trước khi đoán ID"
  - v2: **25/30** (case_accuracy = 0.8333) — cải thiện +2 case sau khi thêm ranh giới xác nhận cho write action
  - v3: **29/30** (case_accuracy = 0.9667) — cải thiện +4 case sau khi làm rõ mô tả tool và tham số
  - **Tổng cộng: cải thiện 9/30 case (30%)** từ v0 → v3

- **Thay đổi hiệu quả nhất:**
  - Nhóm 3 (sai/thiếu tham số): sửa 4 tool description trong `tools.yaml` giúp cải thiện nhiều nhất (+4 case)
  - Nhóm 1 (đoán ID thay vì hỏi): thêm rule "Never guess" trong `system_prompt.md` giúp 3 case `missing_info` đều pass

- **Giới hạn còn lại:**
  - H06 fail do over-clarify (dao động 28-29/30)
  - Một số adversarial case cần review thủ công để xác nhận không có data exfiltration

- **Cách phân công và tích hợp:**
  - TV1 phân tích v0, xác định 3 nhóm lỗi rõ ràng
  - TV2-Tv3-Tv4 mỗi người phụ trách 1 nhóm lỗi và 1 version
  - TV4 tích hợp tất cả và viết report cuối cùng
  - Quy trình: phân tích → hypothesis → sửa artifact → chạy → so sánh → repeat

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

---

### Nguyễn Hà Khuê — 2A202602938

- **Phần việc và file/commit/PR:**
  - Phụ trách v3: sửa description 4 tool trong `tools.yaml` theo giả thuyết #3 (inspect_device bắt buộc set check, search_kb bắt buộc set category, lookup_user lấy asset ID từ kết quả tra cứu, create_ticket giữ ranh giới xác nhận) và bổ sung 3 rule nhỏ trong `system_prompt.md`
  - Chạy v3 và so sánh với v2: +4 case (25→29/30), case_accuracy 0.9667
  - Xây webapp + UI: `webapp.py` (server HTTP chạy tool loop, chọn provider openrouter/openai/anthropic/gemini, chọn version v0–v3, lưu transcript) và giao diện trong `webapp/`
  - Chạy lại toàn bộ v0, v1, v2, v3 trên cùng bộ base_30 để viết `version_log.csv` (prompt_hash/tools_hash, lý do thay đổi, metric trước/sau, run file) và đối chiếu số liệu khi viết `REPORT.md`
  - File: `artifacts/tools.yaml`, `artifacts/system_prompt.md`, `artifacts/version_log.csv`, `artifacts/REPORT.md`, `runs/v3_B_base_*.json`, `webapp.py`, `webapp/`

- **Quyết định, khó khăn và cách xử lý:**
  - Khó khăn: H06 vẫn fail do agent over-clarify, kết quả dao động 28-29/30 giữa các lần chạy
  - Cách xử lý: thêm rule "request đã đủ thông tin thì không hỏi lại summary" vào v3, không cộng thêm rule nữa để tránh over-clarify nặng hơn
  - Quyết định: v3 sửa `tools.yaml` (đổi tools_hash) vì 4 case wrong_arg_value đều do mô tả tham số mơ hồ chứ không chỉ do prompt

- **Điều đã học:**
  - Phải chạy lại toàn bộ các version trên cùng một bộ case thì so sánh giữa các version mới công bằng
  - prompt_hash/tools_hash trong version log là bằng chứng cho thấy artifact nào thực sự đổi ở từng version
  - Webapp/UI cho chọn version và provider giúp demo và so sánh hành vi agent trực tiếp giữa các version

- **AI/công cụ đã dùng và cách kiểm tra:**
  - AI: dùng AI hỗ trợ viết webapp (HTTP server + giao diện) và rà soát report
  - Kiểm tra: chạy lại eval cả 4 version, đối chiếu run file trong `runs/` với số liệu ghi trong `version_log.csv` và `REPORT.md`; chạy thử webapp với từng version v0–v3, xem transcript lưu trong `transcripts/`

- **Thời điểm đã tự nộp URL repo chung trên VLearn:** (điền thời điểm nộp)

---
