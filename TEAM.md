# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Capitalism
- Người đại diện / MSSV:
- Tên repo: `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt:
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên          | MSSV        | GitHub     | Vai trò và công việc                                                                                           | File/commit/PR                                                                                                                                                    |
| ------------------ | ----------- | ---------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phạm Thị Thùy Linh | 2A202602909 | Liine1310h | Prompt và tool contract: cải thiện system prompt, tool schema, routing, clarification và confirmation boundary | [system_prompt.md](starter_v0/artifacts/system_prompt.md), [tools.yaml](starter_v0/artifacts/tools.yaml), [version_log.csv](starter_v0/artifacts/version_log.csv) |

| Bùi Quốc Việt | 2A202602884 | vietbui000 | Chạy adversarial suite; Review đủ 12 case; Kiểm tra `create_ticket`; Kiểm tra `search_device_info`; Kiểm tra `search_kb` và `policy`

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

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
