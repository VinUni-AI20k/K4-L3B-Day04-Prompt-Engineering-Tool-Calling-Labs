# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm:
- Người đại diện / MSSV: Trần Ngọc Khánh / 2A202602923
- Tên repo: `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt:
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Trần Ngọc Khánh | 2A202602923 | Cần bổ sung | Prompt & Iteration Lead: chạy và phân tích v0-v3, cải thiện prompt/tool declarations, ghi version evidence | `abaa696`; `starter_v0/artifacts/{system_prompt.md,tools.yaml,version_log.csv,REPORT.md}`; `starter_v0/{runs,analysis}/` |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Trần Ngọc Khánh — 2A202602923

- Phần việc và file/commit/PR: Prompt & Iteration Lead; thiết lập baseline v0, phân tích failure, xây các hypothesis v1-v3, cải thiện `system_prompt.md` và `tools.yaml`, lưu run/analysis/version log và viết các mục B1, B2, B7 trong report. Evidence kỹ thuật tại commit `abaa696`.
- Quyết định, khó khăn và cách xử lý: TODO — Trần Ngọc Khánh tự viết từ trải nghiệm thực tế; có thể đối chiếu các regression v2 và giới hạn H12 v3 trong report.
- Điều đã học: TODO — Trần Ngọc Khánh tự viết, không dùng nội dung AI tạo thay cho reflection cá nhân.
- AI/công cụ đã dùng và cách kiểm tra: Dùng OpenCode để đọc trace, đề xuất và áp dụng thay đổi prompt/tool declaration, tổng hợp report. Kết quả được tự kiểm tra bằng OpenAI `gpt-4o-mini` trên cùng 30 case cho v0-v3; mọi run đều có `provider_error_cases == 0` và `measured_cases == total_cases == 30`; v3 đạt 29/30, routing và multi-turn đạt 1.0. Tool results và filesystem được rà để phát hiện ticket tạo sai ở v0-v2 và xác nhận v3 không ghi ticket.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
