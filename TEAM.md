# AIOT — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: AIOT
- Người đại diện / MSSV: Hoàng Đức Dũng / 2A202602798
- Tên repo: `K4-L3-DAY04-NhomAIOT-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/hddung-vinai/K4-L3-DAY04-NhomAIOT-PromptEngineeringToolCalling
- Deadline áp dụng và link thông báo đổi hạn nếu có: hạn mặc định 23:59 ngày làm lab 15/09/2026 (Asia/Ho_Chi_Minh) theo [SUBMISSION.md](SUBMISSION.md); chưa ghi nhận thông báo đổi hạn
- Lịch sử bản nộp:
  - `56756cb` (15/09/2026 20:29 +07): bản làm tại lớp — v0–v3 lần đầu, 10 case nhóm, run adversarial. Run của bản này được giữ ở `starter_v0/runs/archive_lab4_attempt1/`.
  - Bổ sung ngày 16/09/2026 (01:26–02:10 +07, **sau hạn mặc định**): làm lại v0–v3 từ starter gốc, thêm v4–v5 (guard xác nhận ở tầng thực thi), chạy lại adversarial và group, transcript CLI, web UI. Phần này commit thành commit mới, không sửa lịch sử `56756cb` theo [RULES.md](RULES.md).

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Hoàng Đức Dũng | 2A202602798 | https://github.com/hddung-vinai | Đại diện nhóm, prompt engineering lead: chạy baseline, đặt giả thuyết và sửa `system_prompt.md`/`tools.yaml` qua v1→v3, guard xác nhận v4–v5, chạy eval/probe, tổng hợp `version_log.csv` và `REPORT.md` | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/confirmation_guard.py`, `starter_v0/tests/test_confirmation_guard.py`, `starter_v0/runs/v0..v5_*.json`, `starter_v0/analysis/`; commit `56756cb` + commit bổ sung |
| Nguyễn Thanh Bình | 2A202602777 | https://github.com/ThanhBinh159 | Eval & safety: viết 10 case nhóm (5 một lượt + 5 nhiều lượt), kiểm thử bộ adversarial 12 case, phân tích an toàn | `starter_v0/data/eval_group.json`; commit _(Bình tự điền)_ |
| Hoàng Đức Minh | 2A202602362 | https://github.com/hoangminh92k3 | UI & tích hợp: chat UI hiển thị tool call/input/kết quả-lỗi/version, transcript hội thoại demo | _(Minh tự điền file/commit thực tế)_ |

## Nhận xét chung

> Bản tổng hợp số liệu từ run thật; nhóm rà lại và chỉnh câu chữ theo ý kiến chung trước khi nộp.

- Kết quả và bằng chứng: bộ base 30 câu `case_accuracy` v0 0.70 → v1 0.8667 → v2 0.9667 → v3 0.9667, giữ 0.9667 ở v4, v5 (`starter_v0/artifacts/version_log.csv`, REPORT mục B1). Bộ adversarial 12 câu: v3 0.6667 và **2 ticket thật bị tạo do tấn công** → v5 0.75 và **0 lệnh ghi do tấn công** (REPORT B4a). Bộ 10 case nhóm trên v5: 0.80 (REPORT B3). Transcript: 5 kịch bản CLI và 1 phiên web UI trên v5 (REPORT B4).
- Thay đổi hiệu quả nhất: (1) v1 viết lại tool declaration — +0.1667 trên base, hết đoán ID và sai `check`; (2) v2 luồng xác nhận 2 bước trong prompt — hết 3 lỗi boundary trên base; (3) v4–v5 guard ở tầng thực thi — chặn ghi dữ liệu từ xác nhận giả mà luồng xác nhận hợp lệ vẫn tạo được ticket.
- Giới hạn còn lại: H19 (môi trường không có trong enum) lật pass/fail theo artifact, probe 5 lần xác nhận không ổn định; G05 hỏi `yes_no` thay vì `choice` cho priority mơ hồ; A04/A11 vẫn FAIL về điểm vì eval chấm lời gọi tool của model dù guard đã chặn ghi; A12/S5 agent vẫn đưa mã nội bộ vào tool web, chỉ được code của tool chặn; guard nhận diện câu đồng ý bằng từ khóa nên có thể chặn nhầm câu trả lời diễn đạt lạ (chặn nhầm thì agent hỏi lại, không ghi sai).
- Cách phân công và tích hợp: phân công dự kiến là Dũng phụ trách vòng lặp prompt/tool và đo lường, Bình phụ trách case nhóm và an toàn, Minh phụ trách UI/transcript; bằng chứng tích hợp vào `starter_v0/artifacts/REPORT.md`. Phần bổ sung ngày 16/09 (làm lại v0–v3, v4–v5, `web_ui.py`, transcript, cập nhật REPORT) được thực hiện trong phiên làm việc của Dũng với Claude Code. Trước khi nộp, nhóm cập nhật bảng Thành viên cho khớp đóng góp và commit thực tế của từng người.

## INDIVIDUAL

Mỗi thành viên tự viết mục của mình. Các dòng in nghiêng là chỗ chính thành viên đó cần điền.

### Hoàng Đức Dũng — 2A202602798

- Phần việc và file/commit/PR:
  - Làm lại v0–v3 từ starter gốc (git `311580e`): run `starter_v0/runs/v0..v3_B_base_openai_20260916T*.json`, giả thuyết và hash trong `starter_v0/artifacts/version_log.csv`, probe độ ổn định trong `starter_v0/analysis/stability_probe/`.
  - Chạy adversarial và 5 transcript CLI (`starter_v0/runs/v3_B_adversarial_*.json`, `starter_v0/transcripts/S1..S5/`, `starter_v0/scripts/run_transcript_scenarios.py`).
  - Guard xác nhận v4–v5: `starter_v0/confirmation_guard.py`, tích hợp vào `starter_v0/agent.py` và `starter_v0/chat.py`, 14 unit test `starter_v0/tests/test_confirmation_guard.py`, run `starter_v0/runs/v4_*`, `starter_v0/runs/v5_*`.
  - Web UI `starter_v0/web_ui.py` và smoke test `starter_v0/scripts/ui_smoke_test.py`, transcript `starter_v0/transcripts/ui/`.
  - Commit: `56756cb` và commit bổ sung _(điền hash)_.
- Quyết định, khó khăn và cách xử lý: _(Dũng tự viết. Các sự kiện có evidence để tham chiếu: quyết định làm lại v0–v3 thay vì giữ bản 15/09; H03 regression ở v2 và probe 5 lần; guard v4 chặn nhầm luồng hợp lệ S2 và sửa ở v5.)_
- Điều đã học: _(Dũng tự viết.)_
- AI/công cụ đã dùng và cách kiểm tra: Dùng Claude Code (model Claude Opus 5) để đọc và so sánh run JSON, đề xuất giả thuyết, sửa `system_prompt.md`/`tools.yaml`, viết guard, unit test, web UI, script transcript và chạy eval. Kiểm tra tự động đã chạy: `scripts/parse_runs.py`, kiểm tra schema `tools.yaml` không đổi tên/enum/required so với starter, probe 5 lần cho case lật kết quả, `python -m unittest discover -s tests` (14 test), so sánh thư mục `tickets/` trước/sau mỗi lần chạy, quét run/transcript tìm credential và API key. _(Dũng bổ sung phần tự rà soát thủ công.)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_

### Nguyễn Thanh Bình — 2A202602777

> Ghi chú cập nhật 16/09: run adversarial được nhắc bên dưới đã chuyển vào `starter_v0/runs/archive_lab4_attempt1/`; REPORT mục B3/B4a/B6 đã được viết lại theo run v3–v5. Bình rà lại và tự sửa mục này cho khớp phần mình thực sự làm.

- Phần việc và file/commit/PR: Viết 10 case tự thiết kế trong `data/eval_group.json` (5 một lượt G01-G05, 5 nhiều lượt MG01-MG05), phủ các phần chưa được bộ base test (tool `policy`, `search_device_info`, service `printing`/`sso`, priority mơ hồ). Chạy và phân tích bộ adversarial 12 case (`runs/*_adversarial_*.json`), tổng hợp mục B3, B4a, B6 (safety review) trong `REPORT.md`.
- Quyết định, khó khăn và cách xử lý: Lần chạy adversarial đầu tiên dùng nhầm `--provider openrouter` (chưa cấu hình key) khiến toàn bộ 12/12 case báo `provider_error`, không dùng được làm bằng chứng — xử lý bằng cách chạy lại đúng `--provider openai` (provider đang hoạt động) trước khi phân tích.
- Điều đã học: Một run có `routing_correct: false` hàng loạt không tự động nghĩa là agent sai — cần đọc `failures`/exception message để phân biệt lỗi cấu hình (provider_error) với lỗi hành vi thật; và với case an toàn, PASS ở routing không chứng minh không có dữ liệu nhạy cảm bị ghi/gửi đi, phải đọc cả `tool_results` và kiểm tra filesystem (thư mục `tickets/`).
- AI/công cụ đã dùng và cách kiểm tra: Dùng Claude (Claude Code) để soạn case theo đúng format `eval_base.json`, đối chiếu enum hợp lệ trong `tools.yaml` trước khi chốt expected output. Kiểm tra bằng cách chạy `run_eval.py --suite group`/`--suite adversarial` và tự đọc lại từng case thay vì chỉ nhìn `case_accuracy` tổng.
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_

### Hoàng Đức Minh — 2A202602362

> Ghi chú cập nhật 16/09: UI hiện có trong repo là `starter_v0/web_ui.py` (làm trong phiên của Dũng, xem mục Nhận xét chung). Minh ghi rõ phần mình thực sự làm và commit tương ứng.

- Phần việc và file/commit/PR: _(Minh tự điền)_
- Quyết định, khó khăn và cách xử lý: _(Minh tự điền)_
- Điều đã học: _(Minh tự điền)_
- AI/công cụ đã dùng và cách kiểm tra: _(Minh tự điền)_
- Thời điểm đã tự nộp URL repo chung trên VLearn: _(điền sau khi nộp)_
