# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Si và Bảy
- Người đại diện / MSSV: 2A202602712
- Tên repo: `K4-L3-DAY04-SivaBay-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/foxxiee04/K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs, nhánh `tamle25`, commit chốt: điền hash commit v3 sau khi merge và trước khi nộp
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Đoàn Phương Linh | 2A202602382 | lingling | cập nhật systemprompt v3 cùng Tuấn | ee4c25d |
| Lê Công Tâm | 2A202602406 | tamle25 | Merge nhánh `foxxiee04` vào `tamle25`, chạy v2/v3 và cập nhật report | `2de41de` merge, |
| Trần Quốc Sáng | 2A202602712 | foxxiee04 | Refine prompt SmartCharging v1 (2 vòng) | `bc9612b`, `87cb13a` |
| Nguyễn Đình Anh Đức | 2A202602856 | ducnda0212 | Dựng baseline v0 cho SmartCharging | `09ebea3` |
| Nguyễn Quang Tuấn | 2A202602470 | tuannq | chạy refine v3` | `ee4c25d` |

## Nhận xét chung

- Kết quả và bằng chứng: case_accuracy trên `data/eval_smartcharging_base.json` đi từ 0.0 (v0, provider_error/misconfig ban đầu) → 0.9667 (v0 chạy được) → 0.9333 (v1, dao động do model) → 1.0 (v2, trên `openai`/`gpt-4o-mini`) → 0.9667 (v3, sau khi đổi sang `ollama`/`gpt-oss:20b` và vá lại các lỗi model yếu hơn để lộ ra). Xem `starter_v0/artifacts/version_log.csv` và các file trong `starter_v0/runs/`.
- Thay đổi hiệu quả nhất: ở v2, cấm đoán `vehicle_id` và ép `response_type=text` cho `clarify` đưa case_accuracy từ 0.9333 lên 1.0. Ở v3, thêm quy tắc bắt buộc gọi tool `clarify` thay vì tự soạn câu trả lời JSON, và tách rõ "yêu cầu đặt lịch" với "xác nhận đặt lịch" cho `create_reservation`, khắc phục các lỗi mới phát sinh khi đổi provider.
- Giới hạn còn lại: `SC08_compare_two_stations` vẫn fail ở v3 — agent (harness một lượt, xem `starter_v0/agent.py`) không phát ra 2 tool call song song cho 2 trạm trong cùng một response khi dùng `gpt-oss:20b` qua Ollama, dù prompt đã có ví dụ cụ thể. Nghi ngờ là giới hạn parallel tool-call của model/kiến trúc single-shot, cần thử vòng lặp nhiều lượt hoặc model khác ở v4.
- Cách phân công và tích hợp: mỗi thành viên làm trên nhánh riêng theo GitHub username (`ducnda0212`, `foxxiee04`, `tuannq`, `lingling`), sau đó merge dần vào `tamle25` làm nhánh tổng hợp và chạy eval/report cuối.

## INDIVIDUAL

Sao chép mục này cho từng thành viên. Mỗi người tự viết phần của mình (quyết định, khó khăn, điều đã học là trải nghiệm cá nhân, không thể điền hộ).

### Đoàn Phương Linh — 2A202602382

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Lê Công Tâm — 2A202602406

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Trần Quốc Sáng — 2A202602712

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Đình Anh Đức — 2A202602856

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Quang Tuấn — 2A202602470

- Phần việc và file/commit/PR: refine v3
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:
