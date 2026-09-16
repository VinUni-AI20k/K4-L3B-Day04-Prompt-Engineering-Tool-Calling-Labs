# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: _(cần điền)_
- Người đại diện / MSSV: _(cần xác nhận)_
- Tên repo: `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling` — repo hiện tên `K4B-DAY04-TRAN-CAO-QUOC-Dinh-2A202602939-PromptEngineeringToolCalling`, cần đổi theo mẫu trước khi nộp
- URL repo, nhánh nộp, commit chốt: https://github.com/kentranpr4-crypto/K4B-DAY04-TRAN-CAO-QUOC-Dinh-2A202602939-PromptEngineeringToolCalling, nhánh `main`, commit chốt _(ghi sau lần push cuối)_
- Deadline áp dụng và link thông báo đổi hạn nếu có: 23:59 ngày 2026-09-15 (Asia/Ho_Chi_Minh); chưa có thông báo đổi hạn

## Thành viên

GitHub ghi theo tên tác giả commit; mỗi người kiểm tra lại username GitHub thật.

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| _(cần điền)_ | _(cần điền)_ | commit: `thailuong1008-coder` | M1 Agent/Prompt: bản nháp system prompt AMR (luật xác nhận, hủy, an toàn) và giả thuyết ban đầu; các luật này được dùng lại ở v1 và v3 | `91756a6` (`artifacts/system_prompt.md`, `version_log.csv`); lưu nguyên văn ở `starter_v0/artifacts/reference/system_prompt_full_m1.md` |
| _(cần điền)_ | _(cần điền)_ | `kentranpr4-crypto` (commit: `Kent Tran`) | M2 Tool/Backend: giao ước tool, dữ liệu giả lập, 6 tool AMR có guard, `tools.yaml` v0 và v2, smoke test, sửa provider Anthropic, `server.py` nối UI với agent thật; tích hợp nhánh, prompt v0/v1/v3 và chạy v0–v3 | `b38e4c2` `e0dcf64` `6279c1f` `d1585af` `66062dc` `696a722` `782e153` `035efa3` `a64e894` `a32a763` `6ab489b` `f062191` `f89a75d` |
| _(cần điền)_ | _(cần điền)_ | commit: `NGUYEN MANH TIEN` | M3 Evaluation/Evidence: bộ `eval_amr_base.json` (30), `eval_amr_adversarial.json` (12), `eval_amr_extension.json` (10), bộ nhóm ban đầu | `f4ae541` (`starter_v0/data/`) |
| _(cần điền)_ | _(cần điền)_ | commit: `truongapep` | M4 UI/Report: `index.html` — khung chat, thanh trạng thái robot, nhật ký tool có input/kết quả/lỗi/version | `656bbbe` (`starter_v0/index.html`) |

## Nhận xét chung

- Kết quả và bằng chứng: mọi run có `provider_error_cases = 0`. Base 0.7333 (v0) → 0.8667 (v1) → 0.9667 (v2) → 0.9333 (v3); adversarial 0.4167 → 0.5833 → 0.6667 → 0.9167; group v3 0.9000; extension v3 0.7000. Chi tiết và đường dẫn run ở [REPORT.md](starter_v0/artifacts/REPORT.md) mục B1 và [version_log.csv](starter_v0/artifacts/version_log.csv).
- Thay đổi hiệu quả nhất: v2 đưa quy tắc về giá trị tham số vào `tools.yaml` (ý nghĩa `confirmed`, khu hạn chế, `response_type`) tăng base 0.8667 → 0.9667; v3 thêm ranh giới an toàn vào prompt tăng adversarial 0.6667 → 0.9167 và là version đầu tiên không tạo mission trái phép (v0–v2 đã tạo MS-0016..MS-0030 khi bị giả mạo xác nhận).
- Giới hạn còn lại: v3 làm tụt AMR30 và ADV06 (hỏi xác nhận thay vì tra khu hạn chế); AMR18 kỳ vọng tra trạng thái robot dù câu hỏi không nhắc lỗi; G04 không chuẩn hóa "robot số 3"; extension 0.7; dữ liệu và mission là giả lập, một provider/model.
- Cách phân công và tích hợp: mỗi vai trò làm trên nhánh hoặc commit riêng rồi merge vào `main` (M1 `91756a6`, M3 qua merge `035efa3`, M4 `656bbbe`). Do thời gian, M2 tích hợp, tách prompt v0 tối giản từ bản nháp của M1, thay các case nhóm trùng câu với bộ base trước khi chạy (`a64e894`) và chạy v0–v3. Bộ base và adversarial của M3 giữ nguyên sau khi chốt.

## INDIVIDUAL

Mỗi thành viên tự viết và commit mục của mình. Các dòng _(tự viết)_ không được viết thay.

### _(Họ và tên M1)_ — _(MSSV)_

- Phần việc và file/commit/PR: _(tự viết)_
- Quyết định, khó khăn và cách xử lý: _(tự viết)_
- Điều đã học: _(tự viết)_
- AI/công cụ đã dùng và cách kiểm tra: _(tự viết)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(tự viết)_

### _(Họ và tên M2)_ — _(MSSV)_

- Phần việc và file/commit/PR: giao ước tool `starter_v0/docs/AMR_TOOL_CONTRACT.md` (`b38e4c2`); 6 tool AMR và guard (`e0dcf64`); dữ liệu giả lập và `tools.yaml` v0 (`6279c1f`); `scripts/smoke_tools.py` (`d1585af`); sửa `providers/anthropic_provider.py` cho anthropic 1.x (`66062dc`); `scripts/check_m2.sh` (`696a722`); `server.py` và nối `index.html` (`782e153`); tích hợp và chạy v0–v3 (`a64e894`, `a32a763`, `6ab489b`, `f062191`, `f89a75d`)
- Quyết định, khó khăn và cách xử lý: _(tự viết)_
- Điều đã học: _(tự viết)_
- AI/công cụ đã dùng và cách kiểm tra: _(tự viết — ghi rõ đã dùng Claude Code và cách tự kiểm tra kết quả)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(tự viết)_

### _(Họ và tên M3)_ — _(MSSV)_

- Phần việc và file/commit/PR: _(tự viết)_
- Quyết định, khó khăn và cách xử lý: _(tự viết)_
- Điều đã học: _(tự viết)_
- AI/công cụ đã dùng và cách kiểm tra: _(tự viết)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(tự viết)_

### _(Họ và tên M4)_ — _(MSSV)_

- Phần việc và file/commit/PR: _(tự viết)_
- Quyết định, khó khăn và cách xử lý: _(tự viết)_
- Điều đã học: _(tự viết)_
- AI/công cụ đã dùng và cách kiểm tra: _(tự viết)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(tự viết)_
