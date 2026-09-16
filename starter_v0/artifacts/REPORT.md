# Day 04 Lab v3 Report — Trợ lý AI của nhóm

- Lĩnh vực tự chọn: IT Helpdesk (trợ lý dịch vụ CNTT nội bộ cho công ty giả lập Northstar Labs).
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: Hỗ trợ nhân viên nội bộ xử lý sự cố CNTT — tra cứu người dùng (`lookup_user`), kiểm tra trạng thái dịch vụ (`check_service_status`), chẩn đoán thiết bị (`inspect_device`), tìm hướng dẫn/chính sách nội bộ (`search_kb`, `policy`), hỏi lại khi thiếu thông tin (`clarify`), và chỉ tạo ticket (`create_ticket`) sau khi người dùng đã xác nhận rõ ràng. Không tự đoán `asset_id`/`employee_id`, không đưa dữ liệu nội bộ ra ngoài khi dùng `search_device_info`.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0: Dùng nguyên bộ IT có sẵn — `starter_v0/data/eval_base.json` (30 câu cơ bản) và `starter_v0/data/eval_adversarial.json` (12 câu an toàn); không chỉnh sửa bộ case. Bộ do starter cung cấp tại commit `2c1a5ec` (Create Level 3B Day04 learner lab).
- Chức năng mở rộng ngoài luồng cơ bản (nếu có; tối đa 10 trong tổng 100 điểm): Chưa xác định — cập nhật nếu nhóm triển khai bonus tool.

## Team

- Team: Enigma
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members: Nguyễn Anh Tuấn (teamlead, UI/transcript/report), Đặng Quang Hưng (baseline & eval infra, v0), Nguyễn Hoàng Anh (prompt & tool declaration, v1), Nguyễn Hữu Thành (lặp v2/v3), Hà Thị Mỹ Linh (bộ case nhóm & an toàn)
- Provider/model: Cập nhật theo run thực tế của từng version (xem `version_log.csv`); v0 baseline chạy bằng `gemini` (`gemini-3.5-flash-lite`).

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent là trợ lý IT Helpdesk nội bộ cho Northstar Labs: tra cứu người dùng, kiểm tra trạng thái dịch vụ, chẩn đoán thiết bị, tìm hướng dẫn/chính sách nội bộ, hỏi lại khi thiếu thông tin và tạo ticket sau khi đã xác nhận. Giới hạn: không xử lý yêu cầu ngoài phạm vi IT Helpdesk, không tự đoán mã tài sản/nhân viên, không tra cứu web cho thông tin nội bộ (chỉ dùng `search_device_info` cho thông tin công khai của thiết bị).

**Link dùng thử:**

> URL: (điền sau khi UI hoàn thiện)

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn hỗ trợ kỹ thuật nội bộ | core |
| check_service_status | Kiểm tra trạng thái một dịch vụ (VPN, email, SSO, wifi, printing) | core |
| inspect_device | Kiểm tra thông tin và chẩn đoán thiết bị theo asset_id | core |
| lookup_user | Tra cứu người dùng trong danh bạ hỗ trợ theo employee_id | core |
| format_incident_report | Trình bày các kết quả đã thu thập thành báo cáo sự cố | core |
| search_device_info | Tìm thông tin công khai về model thiết bị trên web (không dùng dữ liệu nội bộ) | optional |
| policy | Tìm trong chính sách IT nội bộ | optional |
| create_ticket | Tạo ticket hỗ trợ, chỉ sau khi người dùng xác nhận | optional |

## A3. Câu hỏi mẫu

1. VPN của tôi không kết nối được, kiểm tra giúp tôi với.
2. Máy của tôi mã tài sản AST-1042 chạy chậm, bạn kiểm tra được không?
3. Tạo giúp tôi một ticket báo lỗi máy in ở phòng họp tầng 3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
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
