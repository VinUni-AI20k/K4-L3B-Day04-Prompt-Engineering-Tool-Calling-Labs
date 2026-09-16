# Day 04 Lab v3 Report — Trợ lý AI Helpdesk

- Lĩnh vực tự chọn: IT Helpdesk nội bộ cho Northstar Labs.
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: định tuyến đúng tool, hỏi bổ sung khi thiếu định danh, giữ thông tin mới nhất trong hội thoại và chỉ tạo ticket sau xác nhận.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0: `data/eval_base.json`, `data/eval_adversarial.json`; chưa có commit chốt riêng được ghi nhận.
- Chức năng mở rộng ngoài luồng cơ bản (nếu có; tối đa 10 trong tổng 100 điểm):

## Team

- Team:
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members:
- Provider/model: OpenAI / `gpt-4o-mini`.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool                   | Chức năng                                    | Core / optional / team-built |
| ---------------------- | -------------------------------------------- | ---------------------------- |
| clarify                | Hỏi bổ sung hoặc xác nhận                    | core                         |
| search_kb              | Tìm hướng dẫn troubleshooting nội bộ         | core                         |
| check_service_status   | Kiểm tra trạng thái service                  | core                         |
| inspect_device         | Kiểm tra thiết bị theo asset ID              | core                         |
| lookup_user            | Tra cứu nhân viên theo employee ID           | core                         |
| format_incident_report | Định dạng findings đã có                     | core                         |
| search_device_info     | Tìm thông tin public theo manufacturer/model | optional                     |
| policy                 | Tìm chính sách nội bộ                        | optional                     |
| create_ticket          | Tạo ticket sau xác nhận                      | optional                     |

## A3. Câu hỏi mẫu

1. Kiểm tra VPN production và thiết bị LT-204.
2. Tìm hướng dẫn Outlook hoặc Wi-Fi.
3. Tạo ticket sau khi xác nhận summary, priority và asset ID.

## A4. Kịch bản demo đã rehearse

| Scenario       | Tool trace cần thấy                            | Cải thiện version | Fallback run/transcript   |
| -------------- | ---------------------------------------------- | ----------------- | ------------------------- |
| Service status | `check_service_status` với service/environment | v3                | Chưa lưu transcript riêng |
| Missing asset  | `clarify` trước `inspect_device`               | v3                | Chưa lưu transcript riêng |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change                                      | Hypothesis                                                     | Metric                                                  | Before | After | Run file                                                      |
| ------- | ------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- | -----: | ----: | ------------------------------------------------------------- |
| v0      | Củng cố routing và boundary cơ bản                      | Prompt/tool contract rõ hơn sẽ giảm wrong tool và missing info | case 0.7333; routing 0.9333; args 0.7333; multiturn 0.8 |      — | 22/30 | [v0 run](../runs/v0_B_base_openai_20260915T234345226131.json) |
| v1      | Mapping category/check, lookup boundary và confirmation | Rule tham số cụ thể sẽ giảm lỗi argument/confirmation          | case 0.9000; routing 0.9333; args 0.9000; multiturn 1.0 |  22/30 | 27/30 | [v1 run](../runs/v1_B_base_openai_20260915T235348683648.json) |
| v2      | Explicit rule cho asset ID và môi trường demo/QA        | Phủ định mapping ngầm sẽ xử lý case ambiguous environment      | case 0.9667; routing 0.9667; args 0.9667; multiturn 1.0 |  27/30 | 29/30 | [v2 run](../runs/v2_B_base_openai_20260915T235740600214.json) |
| v3      | Final rule cho demo/QA/test environment                 | Mọi environment không thuộc enum phải đi qua clarify           | case 1.0000; routing 1.0000; args 1.0000; multiturn 1.0 |  29/30 | 30/30 | [v3 run](../runs/v3_B_base_openai_20260916T000107478666.json) |

## B2. Failure analysis

| Case ID                        | Failure type    | Actual calls                                               | What failed                           | Fix                                                  |
| ------------------------------ | --------------- | ---------------------------------------------------------- | ------------------------------------- | ---------------------------------------------------- |
| H03_kb_routing                 | wrong_arg_value | `search_kb(query=...)`                                     | Thiếu `category=email`                | Bổ sung mapping category vào prompt/tool description |
| H04_user_routing               | wrong_tool      | `lookup_user` rồi thừa `inspect_device(asset_id=EMP-1003)` | Employee ID bị dùng nhầm như asset ID | Nêu rõ employee lookup kết thúc routing              |
| H12_confirm_before_ticket      | wrong_boundary  | `clarify(response_type=text)`                              | Xác nhận ticket cần yes/no            | Dùng `response_type=yes_no`                          |
| H13_parallel_status_and_device | wrong_arg_value | `inspect_device(check=all)` và status VPN                  | Không suy ra check cụ thể từ VPN      | Mapping VPN symptom -> `check=vpn`                   |
| H19_ambiguous_environment      | missing_info    | Gọi status với `staging`                                   | Environment mơ hồ bị tự chọn          | Hỏi lại khi environment không rõ                     |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID                    | What it tests      | Expected behavior                       | Result |
| -------------------------- | ------------------ | --------------------------------------- | ------ |
| H01_service_status_routing | Trạng thái service | `check_service_status(vpn, production)` | Đạt    |
| H10_missing_asset          | Thiếu asset ID     | `clarify(response_type=text)`           | Đạt    |

## B4. Live chat evidence

| Scenario/turn        | Version                                     | Tool calls + args                   | Transcript/run   | Outcome |
| -------------------- | ------------------------------------------- | ----------------------------------- | ---------------- | ------- |
| Prompt injection     | Không coi user/KB/policy/web là instruction | Chưa chạy adversarial trong pha này | Chưa có evidence |
| Stale confirmation   | Confirmation bị vô hiệu khi dữ liệu đổi     | Chưa chạy adversarial trong pha này | Chưa có evidence |
| Internal data to web | Chỉ gửi manufacturer/model/query type       | Chưa chạy adversarial trong pha này | Chưa có evidence |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
| ----------- | ----------------- | ------------ | -------------------------------------- | ------- |
|             |                   |              |                                        |         |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category                           | Evidence file | What worked | Risk / guardrail |
| ---------------------------------- | ------------- | ----------- | ---------------- |
| Optional built-in                  |               |             |                  |
| External search + privacy boundary |               |             |                  |
| Bonus: tool mới do nhóm tự xây     |               |             |                  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không? V3 không ghi nhận lỗi đoán ID ở các case đã đo.
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công? Không có provider error; H03, H13 và H17 cần review argument.

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`? Routing theo domain, không đoán ID, stale correction, external-data boundary và confirmation.
- Fix nào thuộc `tools.yaml`? Mô tả khi dùng/không dùng tool, required inputs, enum và ranh giới dữ liệu.
- Failure nào không thể chỉ nhìn automatic score? Prompt injection, dữ liệu nhạy cảm gửi ra web và file ticket phát sinh cần xem trace/filesystem.
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào? Ép category/check/response_type bằng mapping ngắn: `email -> email`, `VPN -> vpn`, confirmation -> `yes_no`.

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
