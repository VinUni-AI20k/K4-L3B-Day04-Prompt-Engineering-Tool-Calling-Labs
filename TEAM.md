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
| Lâm Quang Anh Quân | 2A202602467 | awun0105 | Fix missing_info H10, H11, H19, fix parallel tool call, cải thiện UI | `4bd38c7`, PR #4, `cd30f59`, `2c2f713`, `de95476` |

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

- **Phần việc và file/commit/PR:**
  - Vai trò: Sửa routing công cụ (wrong_tool) và quản lý xung đột trong artifact chung
  - File chính trách: `starter_v0/artifacts/system_prompt.md` (từng lượt)
  - Commit tiêu biểu: `c8a72f2` (sửa wrong_tool cases), `e531022` (giải quyết conflict merge system_prompt.md)
  - Lỗi được gán sửa:
    - **H03** (`search_kb` sai category): mô tả rõ ràng cách map topic → category enum trong prompt
    - **H17** (`triage_with_three_sources`): bổ sung rule gọi song song 3 tool khi request cần device + status + KB đồng thời, không gộp chung

- **Quyết định, khó khăn và cách xử lý:**
  - Khó khăn lớn nhất: xác định ranh giới giữa sửa `system_prompt.md` (routing logic) vs sửa `tools.yaml` (schema/mô tả tool). Lúc đầu định sửa description trong tools.yaml, nhưng team quyết định giữ tool definition cố định và chỉ điều chỉnh prompt logic.
  - Conflict trong git khi many branch cùng sửa `system_prompt.md`: đã học cách merge thủ công và kiểm tra lại prompt integrity sau khi resolve. Sử dụng `git diff` để xem rõ thay đổi từng lạn.
  - Xác nhận rằng sửa prompt không làm thay đổi base case behavior của các lỗi khác (ví dụ H10, H11 về missing_info) — yêu cầu rerun version log để đối chiếu.

- **Điều đã học:**
  - Prompt engineering không phải chỉ viết hướng dẫn, mà phải suy luận về cách LLM sẽ parse input, map logic, và quyết định tool. Một câu if-then nhỏ trong prompt có thể ảnh hưởng lớn tới routing của nhiều case.
  - Routing lỗi lặp (H03, H17) thường bắt nguồn từ description công cụ chung chung hoặc logic decision chưa rõ ràng. Cần liệt kê từng trường hợp cụ thể thay vì để LLM tự đoán.
  - Làm nhóm về shared artifact: collaboration qua git commit tốt hơn gửi file zipped. Tuy nhiên cần quy tắc merge rõ ràng (ai sửa gì, rebase hay merge, lúc nào push).

- **AI/công cụ đã dùng và cách kiểm tra:**
  - ChatGPT / Claude: giải thích lý do tại sao `search_kb` với query "Outlook setup" nên dùng `category="email"` thay vì `category="office_tools"`. Kết quả giúp viết prompt rõ ràng hơn.
  - Copilot trong VSCode: autocomplete khi sửa markdown bullet point trong system_prompt.md (không dùng để viết logic).
  - GitHub Desktop + VSCode merge tool: xử lý conflict khi merge branch của Thành viên 2 vào develop. Kiểm tra bằng cách re-run H03/H17 trên v1 sau khi resolve.
  - Công cụ kiểm tra: chạy `python run_eval.py --version v1 --suite base` để kiểm tra H03/H17 PASS sau sửa, và đối chiếu run file trong `runs/v1_B_base_*.json`.

- **Thời điểm đã tự nộp URL repo chung trên VLearn:**
  - Chưa tự nộp (do là team member, không phải group leader). Sẽ nộp cùng lúc với nhóm trưởng Lê Văn Việt trước deadline 23:59 ngày học.

### Lâm Quang Anh Quân — 2A202602467

- Phần việc và file/commit/PR: Fix missing_info H10, H11, H19 (`4bd38c7`, PR #4). Cải thiện UI (hiển thị Markdown, nút Copy) và fix lỗi parallel tool call trong `chat.py` (các commit `cd30f59`, `2c2f713`, `de95476`).
- Quyết định, khó khăn và cách xử lý: Xử lý việc agent tự bịa dữ liệu bằng cách thêm luật chặt chẽ vào system prompt để bắt buộc gọi `clarify`. Fix vòng lặp tool bị ngắt sớm bằng cách chạy toàn bộ tool trong lượt trước khi check `awaiting_user`.
- Điều đã học: Cách ép mô hình hỏi lại thay vì halucinate. Nắm được luồng xử lý tool events và cách render kết quả ra UI.
- AI/công cụ đã dùng và cách kiểm tra: Dùng AI (Antigravity) để hỗ trợ fix logic code UI/tool. Kiểm tra lại bằng cách chạy local UI và transcript.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 09:56:45 16/9/2026.
