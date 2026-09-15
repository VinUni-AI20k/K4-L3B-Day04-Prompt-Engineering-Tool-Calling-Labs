# Day 04 Lab v3 Report — Trợ lý AI của nhóm

- Lĩnh vực tự chọn: IT Helpdesk (Northstar Labs Service Desk)
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: Tiếp nhận yêu cầu kỹ thuật nội bộ, tra cứu tài liệu KB, kiểm tra trạng thái dịch vụ/thiết bị, tra cứu danh bạ nhân viên, hỏi làm rõ khi thiếu thông tin, và xin xác nhận trước khi tạo ticket.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0: `starter_v0/data/eval_base.json`, `starter_v0/data/eval_adversarial.json` (commit: `311580e`)
- Chức năng mở rộng ngoài luồng cơ bản (nếu có; tối đa 10 trong tổng 100 điểm): Chưa có / Đang phát triển

## Team

- Team: Phan-Danh-Dat-2A202602627
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members: Phan Danh Đạt (2A202602627), Trần Gia Khánh (2A202602689), Tô Huy Thông (2A202602608), Nguyễn Đình Anh (2A202602573)
- Provider/model: `openrouter` / `openai/gpt-4o-mini`

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Trợ lý IT Helpdesk hỗ trợ nhân viên Northstar Labs chẩn đoán thiết bị, tra cứu trạng thái hạ tầng dịch vụ (VPN, Email, SSO...), tìm kiếm cẩm nang kỹ thuật, và tạo ticket hỗ trợ. Giới hạn: Không hỗ trợ các tác vụ ngoài phạm vi IT nội bộ, không tự tiện suy đoán mã định danh khi thiếu, và luôn yêu cầu người dùng xác nhận trước khi thực hiện hành động ghi dữ liệu (tạo ticket).

**Link dùng thử:**

> Chạy trực tiếp qua CLI chat: `python chat.py --provider openrouter --version v1`

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung thông tin khi thiếu ID hoặc xin xác nhận hành động | core |
| search_kb | Tìm kiếm hướng dẫn kỹ thuật trong cơ sở tri thức nội bộ | core |
| check_service_status | Kiểm tra trạng thái hoạt động của các dịch vụ nội bộ (VPN, Email, SSO...) | core |
| inspect_device | Kiểm tra thông tin cấu hình và chẩn đoán lỗi phần cứng/mạng của thiết bị | core |
| lookup_user | Tra cứu thông tin nhân viên, phòng ban và tài sản được cấp phát | core |
| format_incident_report | Định dạng các bằng chứng kỹ thuật đã thu thập thành báo cáo sự cố | core |
| create_ticket | Tạo ticket sự cố lên hệ thống sau khi người dùng đã xác nhận | optional |
| read_policy | Đọc các chính sách tuân thủ IT và bảo mật của công ty | optional |
| search_device_info | Tìm kiếm thông số thiết bị trên web ngoài (Tavily Search) | optional |

## A3. Câu hỏi mẫu

1. Dịch vụ VPN môi trường production hiện có hoạt động bình thường không?
2. Máy laptop của tôi bị lỗi không vào được mạng, hãy kiểm tra giúp tôi. (Agent sẽ hỏi lại mã asset_id)
3. Hãy tạo ticket báo lỗi màn hình chớp nháy cho máy DT-087. (Agent sẽ tóm tắt và hỏi xác nhận có tạo ticket không)

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Thiếu mã định danh thiết bị | `clarify(response_type="text")` | v1 sửa dứt điểm lỗi tự đoán asset_id (H10) | `runs/v1_B_base_openrouter_20260915T191743440879.json` |
| Môi trường mơ hồ (demo/test) | `clarify(response_type="choice", options=['production', 'staging'])` | v1 sửa dứt điểm lỗi tự map môi trường (H19) | `runs/v1_B_base_openrouter_20260915T191743440879.json` |
| Yêu cầu tạo ticket sự cố | `clarify(response_type="yes_no")` xin xác nhận trước khi gọi `create_ticket` | v2 xử lý boundary tạo ticket (H12, M05) | Transcripts test trực tiếp trên CLI |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi khởi đầu trước khi sửa prompt và tools | case_accuracy | | 0.70 | starter_v0/runs/v0_B_base_openrouter_20260915T184058272822.json |
| v1 | clarify schema + rules | Thêm quy tắc clarify bắt buộc response_type và options giúp xử lý thiếu ID và ambiguous environment | case_accuracy | 0.70 | 0.73 | starter_v0/runs/v1_B_base_openrouter_20260915T191743440879.json |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả. Ghi dưới đây đường dẫn tới mục đã hoàn thành:

> Link:

## C2. INDIVIDUAL của từng thành viên

Mỗi người tự viết và commit mục INDIVIDUAL của mình trong [TEAM.md](../../TEAM.md), nêu phần việc, bằng chứng kỹ thuật và điều đã học. Không yêu cầu chép lại cùng nội dung ở đây. Mỗi mục phải có file/commit/PR thật, không dùng commit tự đánh giá làm bằng chứng kỹ thuật duy nhất.

> Link các mục INDIVIDUAL:

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

- [ ] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [ ] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).
