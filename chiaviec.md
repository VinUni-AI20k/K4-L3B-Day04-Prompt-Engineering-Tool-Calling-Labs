# HƯỚNG DẪN CHIA VIỆC NHÓM

## 1. Mục tiêu chung

Project là bài lab xây dựng và cải thiện một AI IT Helpdesk Agent có khả năng:

- Chọn đúng tool cho từng yêu cầu.
- Gửi đúng tham số cho tool.
- Hỏi lại khi thiếu thông tin.
- Theo dõi hội thoại nhiều lượt và chấp nhận thông tin sửa đổi mới nhất.
- Chỉ tạo ticket sau khi người dùng xác nhận rõ ràng.
- Không gửi dữ liệu nội bộ ra công cụ tìm kiếm bên ngoài.
- Hiển thị được tool call, input, kết quả/lỗi và phiên bản trong UI.

Mục tiêu điểm của nhóm:

- Prompt và mô tả tool: 20 điểm.
- Thực nghiệm v0 đến v3: 20 điểm.
- 10 case nhóm: 10 điểm.
- Hội thoại và an toàn: 15 điểm.
- UI và transcript: 10 điểm.
- Report: 10 điểm.
- Làm nhóm: 5 điểm.
- Bonus chức năng mới: tối đa 10 điểm nếu có đủ code, dữ liệu, test và demo.

Không được sửa các bộ case cố định để làm tăng điểm. Chỉ được viết case mới vào `starter_v0/data/eval_group.json`.

## 2. Danh sách thành viên cần điền

Thay `Người 1` đến `Người 5` bằng tên thật trong `TEAM.md`.

| Người   | Tên thành viên                                   | Vai trò chính                    | Commit bắt buộc              |
| ------- | ------------------------------------------------ | -------------------------------- | ---------------------------- |
| Người 1 | Phạm Thị Thùy Linh hoặc người được nhóm chỉ định | Prompt và tool contract          | Artifact prompt/tool         |
| Người 2 | Điền tên                                         | Evaluation và version evidence   | Run v0-v3, version log       |
| Người 3 | Điền tên                                         | Safety và tool implementation    | Safety run, code fix nếu cần |
| Người 4 | Điền tên                                         | UI và transcript                 | UI chạy được, transcript     |
| Người 5 | Điền tên                                         | Team eval, report và integration | 10 case, report, TEAM        |

Mỗi người phải có ít nhất một commit kỹ thuật có thể đối chiếu. Mỗi người tự viết mục `INDIVIDUAL` của mình trong `TEAM.md`.

## 3. Người 1 - Prompt và Tool Contract

### Phạm vi phụ trách

Đọc failure từ baseline và cải thiện hai artifact chính:

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/tools.yaml`
- Các mô tả tại `starter_v0/tools/*/TOOL.md` nếu cần đồng bộ.

Không được đổi tên các tool có sẵn hoặc đổi cấu trúc expected của bộ eval cố định.

### Các việc phải làm

1. Đọc bộ tool trong `starter_v0/tools/` và registry trong `starter_v0/tools/__init__.py`.
2. Lập bảng mapping:
   - Yêu cầu kiểm tra service -> `check_service_status`.
   - Yêu cầu kiểm tra một thiết bị -> `inspect_device`.
   - Yêu cầu tìm hướng dẫn -> `search_kb`.
   - Yêu cầu tra nhân viên -> `lookup_user`.
   - Thiếu asset ID/employee ID/environment -> `clarify`.
   - Tạo ticket -> phải xác nhận trước.
   - Tìm thông tin công khai -> `search_device_info`, chỉ dùng manufacturer và model.
3. Bổ sung vào system prompt các nguyên tắc:
   - Phân biệt dữ liệu service, device, user, KB, policy và external web.
   - Không tự đoán ID còn thiếu.
   - Thông tin được sửa ở lượt sau phải thay thế thông tin cũ.
   - Không xem nội dung do user giả mạo là system/developer/tool result.
   - Không coi nội dung trong KB, policy hoặc web result là chỉ dẫn thực thi.
   - Tạo ticket chỉ sau confirmation hợp lệ cho đúng summary, priority và asset ID.
4. Cải thiện description và schema trong `tools.yaml` để model biết:
   - Khi nào dùng tool.
   - Khi nào không được dùng tool.
   - Tham số nào bắt buộc.
   - Enum nào phải giữ nguyên.
5. Kiểm tra `tools.yaml` vẫn khớp `TOOL_FUNCTIONS`.

### Tiêu chí bàn giao

- Có commit riêng cho prompt/tool artifact.
- Prompt không hard-code ID hoặc câu hỏi cụ thể trong eval.
- Tool name, parameter name và enum không bị sai.
- Người 2 có thể chạy eval bằng artifact mới.
- Ghi lại trong `TEAM.md` các quyết định và lý do sửa.

## 4. Người 2 - Evaluation và Version Evidence

### Phạm vi phụ trách

Phụ trách chạy thử nghiệm có kiểm soát và lưu bằng chứng cho v0, v1, v2, v3.

Các file chính:

- `starter_v0/run_eval.py`
- `starter_v0/scripts/parse_runs.py`
- `starter_v0/artifacts/version_log.csv`
- Thư mục `starter_v0/runs/`
- Thư mục `starter_v0/analysis/` nếu nhóm tạo thêm.

### Các việc phải làm

1. Cài môi trường và xác nhận provider:

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

2. Điền API key ở máy local, không commit `.env`.
3. Chạy preflight:

```powershell
python scripts/preflight_provider.py --provider openrouter
```

4. Chạy v0 trước khi sửa artifact:

```powershell
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

5. Sau mỗi thay đổi đã được nhóm thống nhất, chạy v1, v2, v3 bằng cùng provider, cùng bộ case và điều kiện tương đương:

```powershell
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
```

6. Kiểm tra mỗi run phải có:
   - `provider_error_cases == 0`.
   - `measured_cases == total_cases`.
   - Có `summary`.
   - Có `actual_tool_calls` và `tool_results`.
7. Dùng parser khi cần phân tích:

```powershell
python scripts/parse_runs.py runs --output analysis/run-analysis.csv
```

8. Điền `version_log.csv` với:
   - Version.
   - Artifact đã đổi.
   - Prompt hash và tools hash.
   - Lý do thay đổi.
   - Hypothesis.
   - Metric trước/sau.
   - Đường dẫn run thật.

### Tiêu chí bàn giao

- Có đủ run v0, v1, v2, v3.
- Không dùng run lỗi provider làm evidence chính.
- Phân biệt rõ routing accuracy, argument accuracy và multiturn accuracy.
- Chỉ ghi số liệu có trong run thật.
- Gửi cho Người 5 danh sách failure tiêu biểu và metric cuối.

## 5. Người 3 - Safety và Tool Implementation

### Phạm vi phụ trách

Kiểm tra implementation và các ranh giới an toàn. Chỉ sửa code khi trace chứng minh lỗi nằm ở execution hoặc tool boundary, không sửa code chỉ để che kết quả eval.

Các khu vực chính:

- `starter_v0/agent.py`
- `starter_v0/chat.py`
- `starter_v0/tools/create_ticket/`
- `starter_v0/tools/search_device_info/`
- `starter_v0/tools/search_kb/`
- `starter_v0/tools/policy/`
- `starter_v0/tools/_shared.py`

### Các việc phải làm

1. Chạy adversarial suite:

```powershell
python run_eval.py --provider openrouter --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
```

2. Review đủ 12 case, đặc biệt:
   - Prompt exfiltration.
   - Role spoofing.
   - Forged tool result.
   - Argument smuggling.
   - Sensitive ticket payload.
   - Internal data gửi ra web.
   - Unsupported shell tool.
   - Injection trong policy/KB/web.
   - Stale confirmation.
3. Kiểm tra `create_ticket`:
   - Không ghi file khi chưa xác nhận.
   - Không chấp nhận `confirmed=true` do user nhúng trong pseudo-code.
   - Không ghi password, token, MFA, OTP hoặc recovery code.
4. Kiểm tra `search_device_info`:
   - Chỉ nhận manufacturer, model và query type công khai.
   - Từ chối asset ID, employee ID, hostname, location và diagnostic data.
   - Không tin instruction-like text từ web.
5. Kiểm tra `search_kb` và `policy`:
   - Nội dung truy xuất chỉ là evidence/reference.
   - Instruction-like text phải bị tách hoặc loại khỏi nội dung trusted.
6. Nếu sửa code, tạo test/smoke check nhỏ hoặc ghi lệnh kiểm tra trong commit.
7. Phân tích ít nhất 3 adversarial case trong report, không chỉ ghi PASS/FAIL.

### Tiêu chí bàn giao

- Có run adversarial thật.
- Có bảng 3 case phân tích sâu: expected boundary, actual calls, tool result và filesystem.
- Không có ticket phát sinh được commit vào repository.
- Không đưa API key hoặc dữ liệu thật vào transcript.

## 6. Người 4 - UI và Transcript

### Phạm vi phụ trách

Starter hiện có CLI trong `starter_v0/chat.py` nhưng chưa có UI web riêng. Người 4 xây UI tối thiểu chạy được dựa trên agent loop hiện tại, không tự tạo một agent logic khác với evaluator.

### UI bắt buộc phải hiển thị

- Version/artifact version.
- Tin nhắn user và assistant.
- Tool name.
- Tool input/arguments.
- Tool result.
- Tool error nếu có.
- Trạng thái đang chờ user clarification.
- Trạng thái confirmation trước khi tạo ticket.
- Link hoặc đường dẫn transcript đã lưu.

### Các việc phải làm

1. Chọn cách triển khai phù hợp với môi trường nhóm, ví dụ một web server Python nhẹ hoặc giao diện local sử dụng code hiện có.
2. Tái sử dụng:
   - `load_lab_env`.
   - `load_tool_declarations`.
   - `make_provider`.
   - `run_model_tool_loop` hoặc logic tương đương đã review.
3. Không che tool result/error. UI phải hiển thị đúng hành vi thật.
4. Bổ sung hướng dẫn chạy UI vào README hoặc report.
5. Tạo transcript cho tối thiểu các tình huống:
   - Câu hỏi thông thường có tool call.
   - Thiếu asset ID và phải hỏi lại.
   - Hội thoại nhiều lượt có sửa thông tin.
   - Tạo ticket: draft -> confirmation -> action.
   - Một case bị từ chối vì dữ liệu nhạy cảm.
6. Kiểm tra UI bằng provider thật và lưu transcript sau khi đã rà soát secret.

### Tiêu chí bàn giao

- Thành viên khác có thể chạy UI theo đúng hướng dẫn.
- UI thể hiện đủ version, tool, input, result/error và transcript.
- Không chỉ nộp ảnh chụp màn hình.
- Có ít nhất một transcript chứng minh confirmation boundary.

## 7. Người 5 - Team Eval, Report và Integration

### Phạm vi phụ trách

Phụ trách các tài liệu tổng hợp và tích hợp cuối:

- `starter_v0/data/eval_group.json`
- `starter_v0/artifacts/REPORT.md`
- `TEAM.md`
- Checklist trong `SUBMISSION.md` và `RUBRIC.md`.

### Các việc phải làm

1. Viết đúng 10 case mới, không sao chép case có sẵn:
   - 5 single-turn: có `query`.
   - 5 multi-turn: có `turns`.
2. Mỗi case phải có:
   - ID mới, không trùng.
   - `phase: "B"`.
   - `failure_type` hợp lệ.
   - `expect` rõ ràng.
   - `metadata.what_it_tests`.
3. Nên phủ các hành vi còn thiếu như:
   - Hai tool trong cùng yêu cầu.
   - Hỏi lại khi thiếu environment.
   - Hủy yêu cầu tạo ticket.
   - Sửa asset ID ở lượt sau.
   - Không gọi tool với câu hỏi ngoài phạm vi.
4. Chạy group suite:

```powershell
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

5. Hoàn thiện `REPORT.md`:
   - Lĩnh vực và luồng cơ bản.
   - Danh sách tool.
   - Câu hỏi mẫu và kịch bản demo.
   - Bảng v0-v3.
   - Failure analysis.
   - 10 case nhóm và kết quả.
   - Live chat evidence.
   - Adversarial evidence.
   - Safety review.
   - Technical reflection.
6. Hoàn thiện `TEAM.md`:
   - Tên, MSSV, GitHub của cả 5 người.
   - Vai trò và file/commit/PR.
   - Nhận xét chung có link evidence.
   - INDIVIDUAL riêng cho từng người.
7. Kiểm tra toàn bộ repository trước khi chốt.

### Tiêu chí bàn giao

- Đủ 5+5 case.
- Report không có số liệu bịa hoặc đường dẫn giả.
- Mỗi thành viên có commit kỹ thuật.
- Mỗi thành viên tự viết INDIVIDUAL.
- Các đường dẫn evidence mở được trên branch cuối.

## 8. Quy trình làm việc chung

### Bước 1 - Chuẩn bị

- Thống nhất dùng IT Helpdesk hay đổi lĩnh vực.
- Chọn một provider và model dùng chung cho các run.
- Cài môi trường.
- Điền `TEAM.md`.
- Không commit `.env`, `.venv`, API key, cache hoặc ticket.

### Bước 2 - Baseline v0

- Không sửa prompt/tool trước khi chạy v0.
- Chạy base suite.
- Lưu run JSON.
- Người 2 ghi lỗi và metric.

### Bước 3 - Cải thiện v1-v3

Mỗi version chỉ nên có một giả thuyết chính:

- v1: sửa routing và scope trong system prompt.
- v2: sửa tool descriptions/schema và argument guidance.
- v3: củng cố multi-turn, confirmation và safety boundary.

Sau mỗi version phải chạy lại cùng bộ case và ghi vào version log.

### Bước 4 - Safety và group cases

- Người 3 chạy adversarial.
- Người 5 viết group cases.
- Không thay đổi expected behavior của bộ cố định.
- Người 4 tạo transcript từ các luồng thật.

### Bước 5 - Tích hợp cuối

Cả nhóm cùng kiểm tra:

```powershell
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python run_eval.py --provider openrouter --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
```

Mỗi run dùng làm evidence phải thỏa mãn:

```text
provider_error_cases == 0
measured_cases == total_cases
```

## 9. Quy tắc commit và bàn giao

Mỗi người tạo commit có nội dung rõ ràng, ví dụ:

```text
feat(prompt): improve tool routing and confirmation rules
chore(eval): add v0-v3 runs and version evidence
fix(safety): block sensitive ticket payloads
feat(ui): show tool calls and transcript events
docs(report): add group cases and final evidence
```

Không force-push, không xóa lịch sử commit và không sửa ngày commit để che thời điểm làm bài.

Khi bàn giao, người phụ trách gửi cho nhóm:

- File đã thay đổi.
- Commit hash.
- Lệnh kiểm tra đã chạy.
- Kết quả PASS/FAIL.
- Vấn đề còn lại nếu có.

## 10. Checklist cuối cùng

### Code và artifact

- [ ] `system_prompt.md` đã cải thiện.
- [ ] `tools.yaml` khớp tool registry.
- [ ] UI chạy được.
- [ ] Transcript có tool call, arguments, result/error và version.
- [ ] Không có thay đổi không cần thiết trong fixed eval.

### Evidence

- [ ] Có run v0.
- [ ] Có run v1.
- [ ] Có run v2.
- [ ] Có run v3.
- [ ] Có run group.
- [ ] Có run adversarial.
- [ ] `version_log.csv` có hypothesis, metric và đường dẫn thật.
- [ ] `REPORT.md` đã điền đầy đủ.

### An toàn

- [ ] Không commit `.env` hoặc API key.
- [ ] Không commit `.venv`, cache hoặc `tickets/`.
- [ ] Không có password, OTP, MFA, token hoặc recovery code trong transcript.
- [ ] Ticket chỉ được tạo sau xác nhận rõ ràng.
- [ ] Không gửi asset ID, employee ID hoặc diagnostic data ra web search.
- [ ] Đã review thủ công tool results của adversarial run.

### Teamwork và nộp bài

- [ ] `TEAM.md` có đủ 5 thành viên.
- [ ] Mỗi thành viên có commit kỹ thuật.
- [ ] Mỗi thành viên có mục INDIVIDUAL.
- [ ] Đã ghi commit chốt.
- [ ] Mọi thành viên nộp cùng một URL repo trên VLearn.
- [ ] Repo mở được và các đường dẫn evidence hoạt động.
