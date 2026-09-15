# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Viber
- Người đại diện / MSSV: Lê Văn Việt / 2A202602504
- Tên repo: `K4-L3-DAY04-LeVanViet-2A202602504-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/viett06/K4-L3-DAY04-LeVanViet-2A202602504-PromptEngineeringToolCalling — nhánh `develop`
- Deadline áp dụng và link thông báo đổi hạn nếu có: theo [SUBMISSION.md](SUBMISSION.md)

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Lê Văn Việt | 2A202602504 | viett06 | Nhóm trưởng: quản lý nhánh/cấu trúc, chạy eval, sửa prompt/tool sau test, fix missing_info còn lại (H12/A10/G01/G09) | merge PR #1 #2 #4; `starter_v0/artifacts/REPORT.md` |
| Mai Hoàng Anh | 2A202602857 | hoanganh3211 | Sửa wrong_boundary (ticket confirm, injection) + viết 10 case eval group | `e96515a`, `c824272`; `starter_v0/data/eval_group.json` |
| Nguyễn Thành Vinh | 2A202602889 | v1rtuos024 | Fix wrong_tool H03, H04, H17 (KB, lookup_user, triage 3 nguồn) | `a172b7d`, `f8f6555`, PR #5 |
| Nguyễn Văn Diện | 2A202602615 | diendls321 | Fix wrong_tool; xử lý conflict `system_prompt.md` | `c8a72f2`, `e531022` |
| Lâm Quang Anh Quân | 2A202602467 | awun0105 | Fix missing_info H10, H11, H19 | `4bd38c7`, PR #4 |

## Nhận xét chung

- Kết quả và bằng chứng: baseline v0 hợp lệ 21/30 (`runs/v0_B_base_openrouter_20260915T191804639673.json`); base v1/v2 30/30; adversarial v3 12/12; group v3 10/10. Chi tiết trong [starter_v0/artifacts/REPORT.md](starter_v0/artifacts/REPORT.md).
- Thay đổi hiệu quả nhất: không đoán asset/employee ID; `create_ticket` chỉ sau `clarify yes_no` gắn đúng payload; không tách `lookup_user` thành `inspect_device`/`policy`.
- Giới hạn còn lại: chưa re-run base 30 case trên artifact cuối; transcript live từ `chat.py` chưa commit; từng người cần tự viết INDIVIDUAL dưới đây.
- Cách phân công và tích hợp: Vinh/Diện routing, Quân missing_info, Hoàng Anh boundary + group cases, Việt merge/eval/vá lỗi còn lại và report. Artifact chốt: `starter_v0/artifacts/system_prompt.md`, `tools.yaml`, `version_log.csv`.

## INDIVIDUAL

Mỗi người tự viết và tự commit mục của mình. Không nhờ người khác viết hộ.

### Lê Văn Việt — 2A202602504

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Mai Hoàng Anh — 2A202602857

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Thành Vinh — 2A202602889

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Văn Diện — 2A202602615

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Lâm Quang Anh Quân — 2A202602467

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:
