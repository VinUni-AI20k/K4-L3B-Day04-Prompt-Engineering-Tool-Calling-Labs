# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Capitalism
- Người đại diện / MSSV: Phạm Thị Thùy Linh / 2A202602909
- Tên repo: `K4B-Day-4-Capitalism`
- URL repo, nhánh nộp, commit chốt: `https://github.com/Liin1310h/K4B-Day-4-Capitalism`, nhánh `main`
- Deadline áp dụng và link thông báo đổi hạn nếu có: Theo thông báo lớp học

## Thành viên

| Họ và tên          | MSSV        | GitHub     | Vai trò và công việc                                                                                           | File/commit/PR                                                                                                                                                    |
| ------------------ | ----------- | ---------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phạm Thị Thùy Linh | 2A202602909 | Liine1310h | Prompt và tool contract: cải thiện system prompt, tool schema, routing, clarification và confirmation boundary | [system_prompt.md](starter_v0/artifacts/system_prompt.md), [tools.yaml](starter_v0/artifacts/tools.yaml), [version_log.csv](starter_v0/artifacts/version_log.csv) |
| Nguyễn Thùy Linh   | 2A202602497 | LinhNguyen | Evaluation và version evidence: chạy thực nghiệm v0–v3, chuẩn hóa run analysis và duy trì version log         | [run-analysis.csv](starter_v0/run-analysis.csv), [version_log.csv](starter_v0/artifacts/version_log.csv), [runs](starter_v0/runs/)                                |
| Bùi Quốc Việt      | 2A202602884 | vietbui000 | Safety và tool implementation: chạy adversarial suite, kiểm tra ranh giới an toàn, credential guard và catalog | [test_safety.py](starter_v0/tests/test_safety.py), [PERSON3_SAFETY_REPORT.md](starter_v0/analysis/safety/PERSON3_SAFETY_REPORT.md), [tools](starter_v0/tools/)    |
| Lê Thị Duyên       | 2A202602411 | duyenle247 | Team eval, report và integration: xây dựng 10 case nhóm, chạy eval group, tổng hợp REPORT và tích hợp TEAM     | [eval_group.json](starter_v0/data/eval_group.json), [REPORT.md](starter_v0/artifacts/REPORT.md), [TEAM.md](TEAM.md), [group run](starter_v0/runs/v3_B_group_openrouter_20260916T090518831880.json) |

## Nhận xét chung

- **Kết quả và bằng chứng:**
  - Qua 4 vòng lặp từ v0 đến v3, độ chính xác của agent tăng trưởng vượt bậc từ 73.33% (22/30) ở v0 lên tuyệt đối **100.00% (30/30)** ở v3 trên bộ dữ liệu `data/eval_base.json` (bằng chứng: [v3 run](starter_v0/runs/v3_B_base_openai_20260916T000107478666.json)).
  - Bộ 10 test case tự xây dựng của nhóm (`data/eval_group.json`) đạt kết quả xuất sắc **10/10 PASS (100%)**, 0 lỗi provider, routing 1.0, argument 1.0 và multiturn 1.0 (bằng chứng: [group run](starter_v0/runs/v3_B_group_openrouter_20260916T090518831880.json)).
  - Bộ an toàn Adversarial đạt 9/12 PASS (75%), ngăn chặn 100% các hành vi rò rỉ credential, prompt injection và ghi ticket trái phép (bằng chứng: [adversarial run](starter_v0/analysis/safety/v3_B_adversarial_openrouter_20260916T070648272075.json)).
- **Thay đổi hiệu quả nhất:**
  - Việc kết hợp chặt chẽ giữa System Prompt (định nghĩa ranh giới dữ liệu, cấm đoán ID, bắt buộc stale correction) và Tool Contract tường minh trong `tools.yaml` (enum nghiêm ngặt cho category, check, environment).
  - Tầng bảo vệ độc lập (execution guard) trong `tools/_shared.py` và `create_ticket` đảm bảo credential không bị ghi và ticket chỉ được tạo khi có xác nhận tường minh khớp đúng payload.
- **Giới hạn còn lại:**
  - Ở một số truy vấn mô tả lỗi thiết bị quá dài hoặc phức tạp, agent cần thêm một lượt clarification để chốt cấu trúc summary chuẩn trước khi hỏi xác nhận.
  - Danh mục thiết bị công khai (`public_products.json`) hiện là whitelist cố định, cần được mở rộng định kỳ để hỗ trợ nhiều model mới.
- **Cách phân công và tích hợp:**
  - Phân chia công việc theo 5 vai trò chuyên biệt theo hướng dẫn `chiaviec.md`.
  - Toàn bộ kết quả đều có bằng chứng số liệu và file run thật đối chiếu chéo; tích hợp mã nguồn thông qua Git branch và Pull Request minh bạch.

## INDIVIDUAL

### Phạm Thị Thùy Linh — 2A202602909

- Phần việc và file/commit/PR: Phụ trách prompt và tool contract trong [system_prompt.md](starter_v0/artifacts/system_prompt.md) và [tools.yaml](starter_v0/artifacts/tools.yaml). Đã giữ nguyên tên tool, parameter và enum của registry; evidence chạy cùng bộ `data/eval_base.json` được lưu trong [runs](starter_v0/runs/). Commit riêng cho phần artifact: 277c270.
- Quyết định, khó khăn và cách xử lý: Bổ sung mapping service/device/KB/user/policy/external web; yêu cầu `clarify` khi thiếu ID hoặc environment; buộc chọn đúng `category`, `check`, `response_type`; ngăn employee ID bị dùng như asset ID; và chỉ tạo ticket sau xác nhận `yes_no` hiện tại cho đúng summary, priority và asset ID. Khó khăn chính là model vẫn tự map `demo/QA` sang `staging`, nên thêm rule phủ định rõ cho `demo`, `QA`, `test` và team name. Kết quả cuối đạt 30/30, provider errors 0, routing 1.0, argument 1.0, multiturn 1.0.
- Điều đã học: Tool description và schema ảnh hưởng trực tiếp tới argument accuracy, không chỉ việc chọn đúng tool. Khi sửa prompt cần đọc actual tool trace để phân biệt lỗi routing, lỗi tham số và lỗi boundary; không được dùng câu trả lời nghe hợp lý làm bằng chứng duy nhất.
- AI/công cụ đã dùng và cách kiểm tra: Dùng VS Code/Copilot để đọc `chiaviec.md`, registry và các `TOOL.md`, chỉnh artifact bằng patch; dùng evaluator với OpenAI `gpt-4o-mini`; kiểm tra YAML parse, đối chiếu `TOOL_FUNCTIONS`, kiểm tra `provider_error_cases == 0`, `measured_cases == total_cases`, hash artifact và đường dẫn run trong `version_log.csv`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 01:14 16/09/2026

### Nguyễn Thùy Linh — 2A202602497

- Phần việc và file/commit/PR: Phụ trách Evaluation và version evidence. Chịu trách nhiệm trích xuất, phân tích dữ liệu chạy từ các file run JSON trong `starter_v0/runs/` để xây dựng và duy trì hai artifact bằng chứng chính là `[run-analysis.csv](starter_v0/run-analysis.csv)` và `[version_log.csv](starter_v0/artifacts/version_log.csv)`. Commit riêng cho phần bằng chứng: `33ef289`.
- Quyết định, khó khăn và cách xử lý: Xử lý triệt để xung đột dữ liệu và lệch nhãn version giữa các file run rác và file run OpenAI chuẩn (từ v0 đến v3). Đã dùng script kết hợp PowerShell chuẩn hóa dữ liệu 120 case (30 case/phiên bản), đảm bảo trích xuất chính xác 100% các giá trị `artifact_version`, `prompt_hash`, `tools_hash` và tỉ lệ `metric_after` từ v0 (73.33%) nâng dần lên v3 (100%).
- Điều đã học: Hiểu rõ tầm quan trọng của việc đóng gói dữ liệu minh bạch (traceability) trong phát triển Agent. Nhận diện được các Failure Modes (wrong_tool, wrong_boundary, missing_info) thay đổi ra sao qua từng phiên bản prompt/tool contract.
- AI/công cụ đã dùng và cách kiểm tra: Dùng VS Code Terminal (PowerShell), Python script `parse_runs.py` và `Import-Csv` để kiểm tra gom nhóm dữ liệu (`Group-Object version,passed`); đối chiếu trực tiếp hash và đường dẫn run trong `version_log.csv`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 03:30 16/09/2026

### Bùi Quốc Việt — 2A202602884

- Phần việc và file/commit/PR: Tôi phụ trách Safety và Tool Implementation: kiểm tra 12 case adversarial, rà soát xác nhận tạo ticket, credential, dữ liệu nội bộ gửi ra web và injection trong nội dung truy xuất. Các file chính gồm agent.py, chat.py, tools/\_shared.py, implementation của bốn tool liên quan, tests/test_safety.py và analysis/safety/PERSON3_SAFETY_REPORT.md. Commit/PR: bổ sung sau khi commit và tạo PR.
- Quyết định, khó khăn và cách xử lý: Chỉ sửa implementation khi probe/trace chứng minh lỗi ở execution hoặc tool boundary. Bổ sung xác nhận gắn với đúng payload, chặn credential và giới hạn truy vấn web vào danh mục sản phẩm công khai. Các run đầu gặp lỗi tool protocol và quota Groq; đã đổi model, giới hạn output và giãn nhịp request. Giữ nguyên ba case FAIL của run cuối, không sửa đáp án hoặc che lỗi để tăng điểm.
- Điều đã học: Prompt hướng dẫn model chưa đủ để bảo vệ hành động ghi dữ liệu; execution phải kiểm tra quyền xác nhận độc lập. PASS về routing cũng chưa chứng minh an toàn, cần đối chiếu arguments, tool result và filesystem. Nội dung từ KB, policy và web chỉ là tài liệu tham khảo, không được cấp quyền thực thi.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng Codex hỗ trợ phân tích code, đề xuất sửa lỗi, viết test và tổng hợp evidence; dùng Python unittest, Git và Groq để kiểm tra. Kết quả thực thi: 12/12 smoke test PASS; adversarial đo đủ 12 case, 0 lỗi provider, 9 PASS và 3 FAIL. Evidence có snapshot filesystem và hash implementation; không phát sinh ticket trong repo. Các giới hạn và lỗi còn lại được ghi trong báo cáo Người 3.
- Thời điểm đã tự nộp URL repo chung trên VLearn: 07:42 16/09/2026

### Lê Thị Duyên — 2A202602411

- Phần việc và file/commit/PR: Phụ trách Team Eval, Report và Integration. Trực tiếp thiết kế và triển khai 10 test case mới (5 single-turn, 5 multi-turn) trong [eval_group.json](starter_v0/data/eval_group.json); thực thi đánh giá group suite đạt kết quả tuyệt đối **10/10 PASS (100%)** được lưu tại [v3_B_group_openrouter_20260916T090518831880.json](starter_v0/runs/v3_B_group_openrouter_20260916T090518831880.json); tổng hợp và hoàn thiện toàn bộ báo cáo kỹ thuật [REPORT.md](starter_v0/artifacts/REPORT.md) và tài liệu nhóm [TEAM.md](TEAM.md).
- Quyết định, khó khăn và cách xử lý: Thiết kế 10 case nhóm bám sát thực tế nhưng độc lập hoàn toàn với 42 case có sẵn của base và adversarial. Phủ các góc khuất quan trọng: gọi song song 2 tool (`G01`), làm rõ môi trường mơ hồ (`G02`), từ chối câu hỏi ngoài IT (`G03`), tra cứu policy (`G04`), tra cứu thông số công khai (`G05`), đính chính thông tin ở lượt sau (`G06`), hủy tạo ticket (`G07`), bổ sung asset ID bị thiếu (`G08`), chuyển hướng tool (`G09`), và ranh giới xác nhận ticket (`G10`). Cấu hình môi trường chạy mượt mà trên Groq `qwen/qwen3.8-27b`, đạt 0 provider errors, 100% case accuracy, routing 1.0, args 1.0 và multiturn 1.0.
- Điều đã học: Hiểu sâu sắc về quy trình kiểm thử Agent dựa trên các bài test định lượng (Eval-driven Development). Thấy được vai trò trọng yếu của việc đóng gói dữ liệu và tích hợp chéo (Prompt, Schema, Safety Guard, Evidence) để tạo ra sản phẩm hoàn chỉnh, minh bạch và đáp ứng tiêu chuẩn khắt khe của hệ thống.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng Antigravity IDE, Python virtual environment, Groq API (Qwen 3.8-27B), Git để thực thi kiểm thử và chuẩn hóa tài liệu markdown; đối chiếu kết quả qua file JSON run log và kiểm tra tính toàn vẹn của repo.
- Thời điểm đã tự nộp URL repo chung trên VLearn: (Điền thời gian sau khi nộp)
