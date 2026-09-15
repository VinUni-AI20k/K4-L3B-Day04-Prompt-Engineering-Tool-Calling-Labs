# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Enigma
- Người đại diện / MSSV: Nguyễn Anh Tuấn - 2A202602700
- Tên repo: `K4-L3B-Day04-Enigma`
- URL repo, nhánh nộp, commit chốt: https://github.com/harrynguyen127/K4-L3B-Day04-Enigma
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyễn Anh Tuấn| 2A202602700| harrynguyen127| Teamlead. UI, transcript & report: làm UI chat hiện tool call/input/kết quả-lỗi/version, lưu transcript, tổng hợp REPORT.md (cách chạy, trước/sau, giới hạn, link evidence) và điều phối TEAM.md | |
| Nguyễn Hữu Thành | 2A202602813 | nhthanh1106 | Tiếp tục lặp (v2, v3): tiếp nối v1, mỗi vòng 1 giả thuyết + 1 thay đổi chính, chạy lại, so sánh metric/trace, cập nhật version log | |
| Hà Thị Mỹ Linh | 2A202602619 | | Bộ case & an toàn: viết 10 case nhóm (5 một lượt + 5 nhiều lượt) vào eval_group.json, chạy 12 case adversarial, phân tích ≥3 case (hỏi lại/xác nhận/hủy/dữ liệu) | |
| Đặng Quang Hưng | 2A202602719 | hungdq1306 | Baseline & Eval infra (v0): chạy preflight, chạy v0 gốc, đọc lỗi/trace, phân loại failure (sai tool/sai input/thiếu info/nhiều lượt/an toàn). Giao sản phẩm: log v0 + danh sách giả thuyết cho cả nhóm dùng | |
| Nguyễn Hoàng Anh | 2A202602811 | hoanganhIT04 | Prompt & tool declaration (v1): dựa trên giả thuyết của v0, sửa system_prompt.md + tools.yaml, chạy v1, so sánh với v0, ghi vào version_log.csv | starter_v0/artifacts/system_prompt.md, starter_v0/artifacts/tools.yaml, starter_v0/providers/__init__.py, starter_v0/providers/ollama_provider.py, starter_v0/run_eval.py |

## Quy trình v0–v3 và bàn giao

- **Chốt bài toán (trước v0, cả nhóm + Tuấn chốt):** Tuấn (teamlead) chủ trì chốt lĩnh vực, người dùng, nhiệm vụ chính và luồng cơ bản, ghi vào `starter_v0/artifacts/REPORT.md`. Nếu đổi lĩnh vực khỏi Helpdesk, Hưng cần hoàn thiện công cụ/dữ liệu và bộ 30 case cơ bản (20 một lượt + 10 nhiều lượt) *trước khi* chạy v0; nếu giữ Helpdesk thì dùng `data/eval_base.json` có sẵn, bỏ qua bước này.
- **Bàn giao giữa các version:** Hưng chạy v0 → phân loại lỗi, chọn 1 lỗi cụ thể, viết giả thuyết → bàn giao cho Hoàng Anh. Hoàng Anh sửa **một phần chính** của `system_prompt.md`/`tools.yaml` theo giả thuyết, chạy v1, kiểm tra lại toàn bộ case (kể cả case cũ từng đúng) để phát hiện regression, ghi kết quả vào `version_log.csv`, rồi bàn giao giả thuyết/kết quả cho Thành. Thành lặp lại đúng quy trình đó cho v2 rồi v3 (đặt giả thuyết mới → sửa 1 phần chính → chạy → kiểm tra regression → ghi log) trước khi bàn giao toàn bộ 4 run cho Tuấn tổng hợp report.
- **Không chạy 4 lệnh liên tiếp cùng file rồi coi là 4 cải tiến** — giữa mỗi lần chạy phải có bước phân tích và sửa thật, thể hiện qua các commit riêng biệt trên Git.
- **version_log.csv và bảng so sánh trong REPORT.md:** người đang giữ version tại thời điểm chạy (Hưng cho v0, Hoàng Anh cho v1, Thành cho v2/v3) tự ghi ngay dòng của version mình (giả thuyết, thay đổi, chỉ số, đường dẫn run); Tuấn chỉ tổng hợp lại thành bảng so sánh cuối cùng, không tự viết thay nội dung kỹ thuật.
- **Điều kiện run hợp lệ:** mỗi run dùng làm bằng chứng phải có `provider_error_cases == 0` và `measured_cases == total_cases`; nếu lỗi kết nối, người phụ trách version đó phải chạy lại, không tách case lỗi ra để tính điểm phần còn lại.
- **Timebox:** CP1 (18:00–18:20) — Hưng hoàn thành v0 + danh sách giả thuyết. CP2 (18:20–19:05) — Hoàng Anh hoàn thành v1, Thành hoàn thành v2 và v3, cả hai kèm version_log cập nhật.

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Mỗi người tự điền phần của mình (không viết thay người khác).

### Nguyễn Anh Tuấn — 2A202602700

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Hữu Thành — 2A202602813

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Hà Thị Mỹ Linh — 2A202602619

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Đặng Quang Hưng — 2A202602719

- Phần việc và file/commit/PR:
  - Phụ trách **Baseline & Eval infra (v0)** trên branch 0-quanghung.
  - Cài đặt AI Hook logging (setup_hooks.ps1), chạy preflight smoke-test (scripts/preflight_provider.py) PASS.
  - Chạy eval v0 bằng Gemini (gemini-3.5-flash-lite), đạt **30/30 measured cases** với **0 provider error** (Case accuracy: **63.33%**, PASS 19/30).
  - Cải tiến file starter_v0/run_eval.py: bổ sung cơ chế ngắt nghỉ tự động (--batch-size, --batch-delay 90s) và cờ --retry-run-file giúp khắc phục hoàn toàn Rate Limit cho cả nhóm.
  - Xây dựng báo cáo giả thuyết starter_v0/HYPOTHESES_v0.md (phân loại lỗi: wrong_tool, wrong_arg_value, missing_info, wrong_boundary) để giao cho Hoàng Anh làm v1.
  - Ghi nhận kết quả vào starter_v0/artifacts/version_log.csv và tạo tài liệu điều phối nhóm TEAM.md.
  - Files/Commit: HYPOTHESES_v0.md, 
uns/v0_B_base_gemini_20260915T194456857558.json, rtifacts/version_log.csv, 
un_eval.py, TEAM.md.
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Gemini Free API liên tục gặp lỗi Rate Limit (HTTP 429 provider_error) khi gửi 30 prompt liên tiếp, khiến nhiều cases không đo lường được.
  - *Quyết định & Xử lý*: Trực tiếp sửa 
un_eval.py thêm tính năng batch pause (nghỉ 90s sau mỗi 2-4 cases) và cờ --retry-run-file để chỉ retry lại các case dính lỗi mạng mà không làm mất kết quả cũ. Đợt chạy lại thu được 21/30 measured cases sạch lỗi.
- Điều đã học:
  - Nắm vững quy trình dựng Baseline & Infrastructure để đánh giá LLM Agent.
  - Kỹ năng xử lý nghẽn Rate Limit khi tương tác với các LLM Provider API.
  - Cách xây dựng Failure Taxonomy và đề xuất Giả thuyết cải tiến cho Prompt Engineering (v1, v2, v3).
- AI/công cụ đã dùng và cách kiểm tra:
  - AI Assistant (Antigravity IDE - Gemini), Python, Git (branch 0-quanghung).
  - Kiểm tra bằng lệnh python scripts/preflight_provider.py và python run_eval.py.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã tự nộp URL Repo https://github.com/harrynguyen127/K4-L3B-Day04-Enigma trên VLearn lúc 20:10.

### Nguyễn Hoàng Anh — 2A202602811

- Phần việc và file/commit/PR:Thực hiện cải tiến v1 cho IT Helpdesk Agent, tập trung vào routing tool và xử lý thông tin còn thiếu. Chỉnh sửa artifacts/system_prompt.md, artifacts/tools.yaml và run_eval.py; bổ sung providers/ollama_provider.py để hỗ trợ hướng chạy model local. Commit: 95a3a71 — Improve v1 routing and clarification behavior.
- Quyết định, khó khăn và cách xử lý:Dựa trên trace của v0 để xác định các lỗi về chọn tool, tham số và thiếu thông tin. Bổ sung quy tắc phân biệt kiểm tra dịch vụ chung và kiểm tra thiết bị cụ thể, không tự đoán asset_id/employee_id, đồng thời yêu cầu xác nhận trước các thao tác tạo ticket. Khi thử chạy model local, phát hiện môi trường chưa có transformers nên cần bổ sung dependency.
- Điều đã học:Học cách cải thiện agent dựa trên evidence từ evaluation thay vì sửa toàn bộ hệ thống. Hiểu rõ hơn cách system prompt và tool description ảnh hưởng đến routing, argument và clarification của agent.
- AI/công cụ đã dùng và cách kiểm tra:Sử dụng ChatGPT để phân tích trace, đề xuất thay đổi prompt/tool schema và hỗ trợ xử lý Git. Sử dụng Python/PowerShell để chạy evaluation và kiểm tra model local; kiểm tra kết quả thông qua log, git status, commit và push lên GitHub.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 20:04:26 15/9/2026
