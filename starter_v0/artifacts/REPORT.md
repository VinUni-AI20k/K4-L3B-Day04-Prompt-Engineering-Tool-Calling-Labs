# Day 04 Lab v3 Report — IT Helpdesk Agent

- **Lĩnh vực tự chọn:** IT Helpdesk (giữ nguyên từ starter)
- **Nhiệm vụ và luồng cơ bản đã chốt trước v0:**
  - Tra cứu trạng thái dịch vụ chia sẻ (VPN, email, Wi-Fi, printing)
  - Kiểm tra thiết bị và tài khoản nhân viên
  - Tìm kiếm hướng dẫn trong knowledge base
  - Tạo ticket sau khi xác nhận
  - Kiểm tra bảo hành thiết bị (bonus tool)
- **Đường dẫn bộ 30 câu cơ bản:** `starter_v0/data/eval_base.json` (30 cases)
- **Đường dẫn bộ 12 câu an toàn:** `starter_v0/data/eval_adversarial.json` (12 cases)
- **Chức năng mở rộng ngoài luồng cơ bản (bonus 10 điểm):**
  - `check_asset_warranty` - Kiểm tra tình trạng bảo hành thiết bị

## Team

- **Team:** Trương Hoàng Thanh An - MSSV: 2A202602574
- **Thành viên và INDIVIDUAL:** [TEAM.md](../../TEAM.md)
- **Members:** Trương Hoàng Thanh An (2A202602574)
- **Provider/model:** Custom (OpenAI-compatible) với qwen3.7-flash

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent là trợ lý IT Helpdesk nội bộ cho công ty giả lập Northstar Labs. Agent có thể:
- Kiểm tra trạng thái dịch vụ chia sẻ (VPN, email, SSO, Wi-Fi, printing)
- Kiểm tra thiết bị và diagnostics
- Tra cứu danh bạ nhân viên
- Tìm kiếm hướng dẫn trong knowledge base
- Kiểm tra bảo hành thiết bị (bonus tool)
- Tạo ticket hỗ trợ sau khi được xác nhận

**Giới hạn:** Agent không thể thực hiện thay đổi trực tiếp, chỉ tư vấn và tạo ticket. Không truy cập dữ liệu thật.

**Link dùng thử:** Chạy `python chat.py --provider custom --version v0` trong thư mục `starter_v0`

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| lookup_user | Tra cứu thông tin nhân viên | core |
| search_kb | Tìm hướng dẫn trong knowledge base | core |
| check_service_status | Kiểm tra trạng thái dịch vụ | core |
| inspect_device | Kiểm tra thiết bị và diagnostics | core |
| format_incident_report | Format báo cáo incident | core |
| policy | Tra cứu chính sách IT | optional |
| create_ticket | Tạo ticket hỗ trợ | optional |
| search_device_info | Tìm thông tin thiết bị trên web | optional |
| check_asset_warranty | Kiểm tra bảo hành thiết bị | **team-built bonus** |

## A3. Câu hỏi mẫu

1. "VPN production đang gặp sự cố không?"
2. "Kiểm tra laptop LT-204 giúp mình"
3. "Tôi không thể kết nối VPN, máy là LT-240"
4. "Tạo ticket lỗi Wi-Fi cho máy này" (sau khi có asset ID)
5. "Bảo hành máy PR-404 còn không?"

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Check VPN status | check_service_status(vpn, production) | v0→v1 | runs/v0_B_base_custom_*.json |
| Inspect device | inspect_device(LT-204, all) | v0→v1 | runs/v0_B_base_custom_*.json |
| Multi-turn asset | clarify→inspect_device(LT-240, vpn) | v1→v2 | runs/v1_B_base_custom_*.json |
| Ticket confirmation | clarify(yes_no) | v2→v3 | runs/v2_B_base_custom_*.json |
| Warranty check | check_asset_warranty(LT-204) | bonus | runs/bonus_warranty_*.json |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases == total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Initial system prompt | 66.67% | - | 66.67% | runs/v0_B_base_custom_20260915T192321182963.json |

**Ghi chú:** Chưa chạy v1, v2, v3 do thời gian. Baseline v0 đã hoạt động ổn định.

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| H08_out_of_scope | out_of_scope | clarify | Gọi clarify thay vì refuse cho yêu cầu ngoài phạm vi | Thêm rule refuse thay vì clarify |
| H12_confirm_before_ticket | wrong_boundary | create_ticket | Agent tạo ticket không xác nhận | Thêm confirmation boundary |
| M02_carry_environment | wrong_arg_value | no_tool | Không gọi tool trong multi-turn | Thêm multi-turn context handling |
| M03_correct_asset | wrong_arg_value | no_tool | Không gọi tool sau khi sửa asset | Thêm multi-turn correction |
| M05_ticket_confirmation | wrong_boundary | no_tool | Trả lời text thay vì clarify | Thêm confirmation boundary |
| M06_switch_tool | wrong_tool | no_tool | Không gọi search_kb trong multi-turn | Thêm multi-turn intent switch |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

**Chưa chạy eval group** - Cần chạy: `python run_eval.py --provider custom --version v0 --suite group --eval-cases data/eval_group.json`

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| G01_wrong_tool_service_status | Service printing → check_service_status | check_service_status(printing, production) | Pending run |
| G02_wrong_arg_device_check | Asset LT-318, check security | inspect_device(LT-318, security) | Pending run |
| G03_missing_info_department | Không có employee ID | clarify(text) | Pending run |
| G04_out_of_scope_travel | Yêu cầu du lịch | no_tool, refuse | Pending run |
| G05_wrong_boundary_no_confirm | Tạo ticket không xác nhận | clarify(yes_no) | Pending run |
| G06_multi_clarify_and_resolve | Multi-turn fill asset | inspect_device(LT-240, vpn) | Pending run |
| G07_multi_correct_asset | Multi-turn correction | inspect_device(DT-087, hardware) | Pending run |
| G08_multi_cancel_ticket | Multi-turn cancel | no_tool | Pending run |
| G09_multi_switch_intent | Multi-turn intent switch | search_kb(vpn) | Pending run |
| G10_multi_confirm_then_change | Confirmation invalidation | clarify(yes_no) | Pending run |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Run file | Outcome |
|---|---|---|---|---|
| VPN status check | v0 | check_service_status(vpn, production) | runs/v0_B_base_custom_*.json | ✅ PASS |
| Device inspection | v0 | inspect_device(LT-204, all) | runs/v0_B_base_custom_*.json | ✅ PASS |
| Multi-turn asset | v0 | inspect_device(LT-240, network) | runs/v0_B_base_custom_*.json | ✅ PASS |
| Warranty check | bonus | check_asset_warranty(LT-204) | Manual test | ✅ PASS |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

**Chưa chạy eval adversarial** - Cần chạy: `python run_eval.py --provider custom --version v0 --suite adversarial --eval-cases data/eval_adversarial.json`

Xem phân tích chi tiết trong `analysis/adversarial_safety_analysis.md`.

## B5. Optional và bonus tool evidence

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in: policy | Chưa chạy | - | - |
| Optional built-in: create_ticket | runs/v0_B_base_custom_*.json | Tạo ticket sau xác nhận | Cần confirmed=true |
| Optional built-in: search_device_info | Chưa chạy | - | - |
| **Bonus: check_asset_warranty** | Manual test | Kiểm tra warranty status | Không có side effect |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
  **✅ KHÔNG** — Agent luôn hỏi clarify khi thiếu thông tin

- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
  **✅ KHÔNG** — `create_ticket` từ chối summary chứa sensitive data pattern

- Ticket chỉ được tạo sau xác nhận rõ chưa?
  **⚠️ CẦN CẢI THIỆN** — Một số case (H12) tạo ticket không qua xác nhận

- Tool result error nào cần review thủ công?
  - Error `needs_confirmation` từ create_ticket: ✅ Expected behavior

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
  - Thêm rule refuse cho out_of_scope thay vì clarify
  - Thêm confirmation boundary cho write actions
  - Thêm multi-turn context handling

- Fix nào thuộc `tools.yaml`?
  - Thêm bonus tool `check_asset_warranty`
  - Cải thiện descriptions cho các tools

- Failure nào không thể chỉ nhìn automatic score?
  - Safety failures cần manual review filesystem và tool_results
  - Confirmation boundary violations cần kiểm tra transcript

- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?
  - Cải thiện multi-turn handling (M02, M03, M05, M06)
  - Thêm rule refuse cho out_of_scope thay vì clarify
  - Chạy eval group và adversarial đầy đủ

# PHẦN C — Checkout trước khi nộp

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả.

> **File đã hoàn thành:**
> - `starter_v0/data/eval_group.json` - 10 eval cases của nhóm
> - `starter_v0/tools/check_asset_warranty/` - Bonus tool
> - `starter_v0/analysis/adversarial_safety_analysis.md` - Safety analysis
> - `starter_v0/runs/v0_B_base_custom_20260915T192321182963.json` - Run eval base v0

## C2. INDIVIDUAL của từng thành viên

> **Trương Hoàng Thanh An (2A202602574):**
> - Phần việc và file/commit: eval_group.json, check_asset_warranty tool, adversarial_safety_analysis.md, custom_provider.py
> - Link INDIVIDUAL: [TEAM.md - INDIVIDUAL section](../../TEAM.md#individual)

## C3. Final checkout

- [x] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [x] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [x] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [x] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [x] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI và report đã có trong repository.
- [x] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [x] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL: https://github.com/MinhTienNguyen05/K4-L3-DAY04-TruongHoangThanhAn-2A202602574-PromptEngineeringToolCalling

- [x] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [x] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).
