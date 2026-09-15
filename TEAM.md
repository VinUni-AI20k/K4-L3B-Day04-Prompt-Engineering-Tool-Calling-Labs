# AIOT — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: AIOT
- Người đại diện / MSSV: Hoàng Đức Dũng / 2A202602798
- Tên repo: `K4-L3-DAY04-NhomAIOT-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/hddung-vinai/K4-L3-DAY04-NhomAIOT-PromptEngineeringToolCalling
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Hoàng Đức Dũng | 2A202602798 | (đại diện nhóm) | Prompt engineering lead: chạy baseline v0, đặt giả thuyết và sửa `system_prompt.md`/`tools.yaml` qua v1→v3, ghi `version_log.csv`, tổng hợp `REPORT.md` | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/v0..v3_*.json` |
| Nguyễn Thanh Bình | 2A202602777 | https://github.com/ThanhBinh159 | Eval & safety: viết 10 case nhóm (5 một lượt + 5 nhiều lượt), chạy bộ adversarial 12 case, phân tích an toàn (chống đoán ID, chống rò rỉ dữ liệu, chống giả mạo xác nhận) | `starter_v0/data/eval_group.json`, `starter_v0/runs/*_adversarial_*.json`, mục B3/B4a/B6 trong `REPORT.md` |
| Hoàng Đức Minh | 2A202602362 | https://github.com/hoangminh92k3 | UI & tích hợp: hoàn thiện chat UI hiển thị tool call/input/kết quả-lỗi/version, lưu transcript hội thoại demo, hỗ trợ tổng hợp mục A trong `REPORT.md` | UI chat app, `starter_v0/transcripts/`, mục A/B4 trong `REPORT.md` |

## Nhận xét chung

- Kết quả và bằng chứng: Sau 3 vòng cải thiện, `case_accuracy` trên bộ base 30 câu tăng từ 0.70 (v0) lên 0.90 (v3); chi tiết và run file trong `starter_v0/artifacts/version_log.csv` và `starter_v0/artifacts/REPORT.md` (mục B1, B2).
- Thay đổi hiệu quả nhất: Rule bắt buộc `clarify(response_type=yes_no)` trước mọi `create_ticket` (thêm ở v1) — triệt tiêu hoàn toàn nhóm lỗi `wrong_boundary` (tạo ticket không xác nhận) ngay từ vòng đầu, không gây regression ở các vòng sau.
- Giới hạn còn lại: `H19_ambiguous_environment` (agent đôi khi vẫn tự chọn `production` cho từ mơ hồ "demo" thay vì hỏi lại) và `M09_confirmation_invalidated` (đôi khi tách 1 yêu cầu xác nhận thành 2 lệnh `clarify` — nghi là nhiễu tự nhiên của model hơn là lỗi prompt); xem B7 trong `REPORT.md`.
- Cách phân công và tích hợp: Dũng phụ trách vòng lặp prompt/tool + đo lường (v0-v3); Bình phụ trách bộ case tự viết và kiểm thử an toàn; Minh phụ trách UI/transcript. Cả ba tích hợp bằng chứng chung vào `starter_v0/artifacts/REPORT.md`, mỗi người tự viết mục INDIVIDUAL của mình bên dưới.

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Hoàng Đức Dũng — 2A202602798

- Phần việc và file/commit/PR: Chạy baseline v0 (`runs/v0_B_base_openai_20260915T194620390021.json`), phân tích 3 nhóm lỗi (wrong_boundary, missing_info, wrong_tool), đặt giả thuyết và sửa `artifacts/system_prompt.md` + `artifacts/tools.yaml` qua v1 → v3, chạy lại eval mỗi vòng và ghi đầy đủ vào `artifacts/version_log.csv`. Tổng hợp `artifacts/REPORT.md` phần A, B1, B2, B6, B7.
- Quyết định, khó khăn và cách xử lý: Ở v3 lần thử đầu, sửa cùng lúc nhiều rule khiến 3 case mục tiêu hết fail nhưng lại gây regression ở 4 case khác đang pass (case_accuracy giảm từ 0.8667 xuống 0.8333) — xử lý bằng cách rollback về đúng trạng thái v2, sau đó làm lại theo nguyên tắc "một giả thuyết – một thay đổi chính mỗi vòng", kết quả cuối đạt 0.90 mà không mất case nào đã pass.
- Điều đã học: Sửa prompt để fix một lỗi cụ thể có thể gây side-effect trên các case tưởng như không liên quan, vì model đọc toàn bộ prompt như một khối chứ không áp dụng rule tách biệt từng phần; cần luôn re-run toàn bộ suite sau mỗi thay đổi, không chỉ kiểm tra case mục tiêu. Cũng học được rằng rule "giá trị phải đúng định dạng" chưa đủ — cần thêm ràng buộc "phải xuất hiện literal trong hội thoại" để chặn việc model bịa ID hợp lệ về hình thức nhưng không có thật.
- AI/công cụ đã dùng và cách kiểm tra: Dùng Claude (Claude Code) để đọc/phân tích run JSON, đề xuất và áp dụng chỉnh sửa `system_prompt.md`/`tools.yaml`. Kiểm tra bằng cách tự chạy `run_eval.py` sau mỗi lần sửa, đối chiếu `case_accuracy`/`failure_counts` và đọc thủ công `actual_tool_calls` của từng case fail trước khi kết luận nguyên nhân, không chỉ tin vào điểm số tự động.
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_

### Nguyễn Thanh Bình — 2A202602777

- Phần việc và file/commit/PR: Viết 10 case tự thiết kế trong `data/eval_group.json` (5 một lượt G01-G05, 5 nhiều lượt MG01-MG05), phủ các phần chưa được bộ base test (tool `policy`, `search_device_info`, service `printing`/`sso`, priority mơ hồ). Chạy và phân tích bộ adversarial 12 case (`runs/*_adversarial_*.json`), tổng hợp mục B3, B4a, B6 (safety review) trong `REPORT.md`.
- Quyết định, khó khăn và cách xử lý: Lần chạy adversarial đầu tiên dùng nhầm `--provider openrouter` (chưa cấu hình key) khiến toàn bộ 12/12 case báo `provider_error`, không dùng được làm bằng chứng — xử lý bằng cách chạy lại đúng `--provider openai` (provider đang hoạt động) trước khi phân tích.
- Điều đã học: Một run có `routing_correct: false` hàng loạt không tự động nghĩa là agent sai — cần đọc `failures`/exception message để phân biệt lỗi cấu hình (provider_error) với lỗi hành vi thật; và với case an toàn, PASS ở routing không chứng minh không có dữ liệu nhạy cảm bị ghi/gửi đi, phải đọc cả `tool_results` và kiểm tra filesystem (thư mục `tickets/`).
- AI/công cụ đã dùng và cách kiểm tra: Dùng Claude (Claude Code) để soạn case theo đúng format `eval_base.json`, đối chiếu enum hợp lệ trong `tools.yaml` trước khi chốt expected output. Kiểm tra bằng cách chạy `run_eval.py --suite group`/`--suite adversarial` và tự đọc lại từng case thay vì chỉ nhìn `case_accuracy` tổng.
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_

### Hoàng Đức Minh — 2A202602362

- Phần việc và file/commit/PR: Hoàn thiện chat UI hiển thị tool call, input, kết quả/lỗi và phiên bản (v0-v3) theo yêu cầu README; lưu transcript cho các hội thoại yêu cầu (thông thường, thiếu thông tin, nhiều lượt, hành động ghi dữ liệu). Hỗ trợ tổng hợp mục A (giới thiệu agent) và B4 (live chat evidence) trong `REPORT.md`.
- Quyết định, khó khăn và cách xử lý: _(điền cụ thể theo khó khăn thực tế khi làm UI, ví dụ: xử lý hiển thị lỗi tool_result khác với lỗi routing, hoặc đồng bộ version artifact hiển thị trên UI với run thật)_
- Điều đã học: _(điền theo trải nghiệm thực tế, ví dụ: khác biệt giữa "agent chọn đúng tool" và "hành động thực sự thành công" chỉ thấy rõ khi hiển thị đầy đủ tool_result trên UI)_
- AI/công cụ đã dùng và cách kiểm tra: Dùng Claude (Claude Code) hỗ trợ dựng UI; kiểm tra bằng cách tự chạy thử từng kịch bản demo trên UI (câu hỏi thường, thiếu thông tin, sửa/hủy giữa hội thoại, tạo ticket) và đối chiếu với run JSON tương ứng để đảm bảo UI hiển thị đúng thực tế agent đã làm.
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_
