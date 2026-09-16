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
| Nguyễn Hà Khuê | 2A202602938 | [@khuenghal](https://github.com/khuenghal) | **TV4 - v3 + tích hợp**: Sửa artifact theo giả thuyết #3, chạy v3, tổng hợp version_log.csv, viết report, hoàn thiện repo, chạy adversarial | `artifacts/tools.yaml`, `runs/v3_B_base_*.json`, `artifacts/REPORT.md` |

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

### Lê Đức Hùng — 2A202602849

- **Phần việc và file/commit/PR:**
  - Phụ trách v2: sửa `system_prompt.md` theo giả thuyết #2, thêm mục Write actions and confirmation
  - Chạy v2 và so sánh với v1: +2 case (23→25/30), `multiturn_accuracy` lên 1.0
  - Đề xuất giả thuyết #3: "Sai/thiếu tham số" — tool gọi đúng nhưng tham số không đầy đủ
  - Phụ trách UI chat: tạo giao diện hiện tool call, input, kết quả/lỗi, version
  - File: `artifacts/system_prompt.md`, `runs/v2_B_base_*.json`, `ui/`

- **Quyết định, khó khăn và cách xử lý:**
  - Khó khăn: H12 vẫn fail (agent hỏi bổ sung summary thay vì hỏi yes/no)
  - Cách xử lý: chuyển H12 sang giả thuyết #3 cho v3 xử lý
  - Quyết định: tập trung vào confirmation boundary, không sửa H12 ngay

- **Điều đã học:**
  - Write action (create_ticket) cần confirmation riêng cho từng payload
  - Confirmation cũ mất hiệu lực khi payload thay đổi
  - UI cần hiện đủ: tool name, args, result/error, version để debug

- **AI/công cụ đã dùng và cách kiểm tra:**
  - AI: dùng AI viết UI với streaming response
  - Kiểm tra: chạy thử với nhiều loại query (bình thường, thiếu thông tin, multi-turn)

- **Thời điểm đã tự nộp URL repo chung trên VLearn:** 07:16:21 16/9/2026

---
