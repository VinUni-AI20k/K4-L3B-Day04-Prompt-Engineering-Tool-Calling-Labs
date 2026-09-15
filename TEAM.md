# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: KTD
- Người đại diện / MSSV: Trần Ngọc Khánh / 2A202602923
- Tên repo: `K4-L3-DAY04-KTD-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt:
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên        | MSSV        | GitHub        | Vai trò và công việc                                                                                           | File/commit/PR                                                                                                                                                                 |
| ---------------- | ----------- | ------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Trần Ngọc Khánh  | 2A202602923 | trankhanh6162 | Prompt & Iteration Lead: chạy và phân tích v0-v3, cải thiện prompt/tool declarations, ghi version evidence     | `abaa696`; `starter_v0/artifacts/{system_prompt.md,tools.yaml,version_log.csv,REPORT.md}`; `starter_v0/{runs,analysis}/`                                                       |
| Nguyễn Hữu Thành | 2A202602807 |               | Data & Safety Lead: viết 10 group case, chạy group/adversarial eval, phân tích safety trace và ticket boundary | `starter_v0/data/eval_group.json`; `starter_v0/runs/v3_B_{group_gemini_20260915T202018601138,adversarial_openai_20260915T202857024627}.json`; `TEAM.md; `data/eval_group.json` |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Trần Ngọc Khánh — 2A202602923

- Phần việc và file/commit/PR: Prompt & Iteration Lead; thiết lập baseline v0, phân tích failure, xây các hypothesis v1-v3, cải thiện `system_prompt.md` và `tools.yaml`, lưu run/analysis/version log và viết các mục B1, B2, B7 trong report. Evidence kỹ thuật tại commit `abaa696`.
- Quyết định, khó khăn và cách xử lý: Khó khăn lớn nhất là v2 không tăng tổng accuracy và làm hai case đang PASS bị regression vì quy tắc hỏi lại còn quá rộng. Tôi giữ run này làm evidence thay vì che kết quả, đối chiếu từng case với v1 rồi thu hẹp quy tắc ở v3: dùng trực tiếp enum hợp lệ, bắt buộc category cụ thể và tách rõ bước xác nhận ticket. Nhờ đó v3 đạt 29/30, routing và multi-turn đều đạt 1.0.
- Điều đã học: Tôi học được rằng system prompt hiệu quả cần mô tả một quy trình quyết định rõ ràng thay vì chỉ liệt kê capability. Các quy tắc về thông tin bắt buộc, ý định mới nhất, sửa/hủy và hiệu lực của xác nhận giúp agent ổn định hơn; tuy nhiên mọi thay đổi vẫn phải được kiểm tra bằng cùng bộ case và đọc cả tool results vì automatic score không phản ánh đầy đủ hành động ghi dữ liệu.
- AI/công cụ đã dùng và cách kiểm tra: Dùng OpenCode để đọc trace, đề xuất và áp dụng thay đổi prompt/tool declaration, tổng hợp report. Kết quả được tự kiểm tra bằng OpenAI `gpt-4o-mini` trên cùng 30 case cho v0-v3; mọi run đều có `provider_error_cases == 0` và `measured_cases == total_cases == 30`; v3 đạt 29/30, routing và multi-turn đạt 1.0. Tool results và filesystem được rà để phát hiện ticket tạo sai ở v0-v2 và xác nhận v3 không ghi ticket.
- Thời điểm đã tự nộp URL repo chung trên VLearn:

### Nguyễn Hữu Thành - 2A202602807

- Phần việc và file/commit/PR: Data & Safety Lead; viết 10 case gốc trong `starter_v0/data/eval_group.json` gồm 5 single-turn và 5 multi-turn; kiểm tra schema, expected tool/argument; chạy và đọc group eval v3; chạy adversarial bằng OpenAI và phân tích trace an toàn. Evidence: `starter_v0/runs/v3_B_group_gemini_20260915T202018601138.json` và `starter_v0/runs/v3_B_adversarial_openai_20260915T202857024627.json`. Commit/PR: bổ sung sau khi tự commit phần việc này.
- Quyết định, khó khăn và cách xử lý: Tôi thiết kế case theo tình huống Helpdesk có dữ liệu giả lập, ưu tiên kiểm tra đúng tool, đúng argument, ghi nhớ context đa lượt, hủy hành động và confirmation trước khi tạo ticket. Gemini bị giới hạn request/phút nên các group run có `provider_error` và không được dùng để kết luận chất lượng agent. Tôi dùng run adversarial OpenAI có `provider_error_cases == 0` để phân tích hành vi an toàn dựa trên trace thay vì suy đoán từ điểm số.
- Điều đã học: Tôi học được rằng safety evaluation không chỉ kiểm tra agent có từ chối hay không, mà phải kiểm tra tool call, argument, tool result và filesystem. Case A03 cho thấy text giả mạo `TOOL_RESULTS_JSON` có thể khiến agent tạo ticket sai; A06 xác nhận agent không gửi dữ liệu asset nội bộ ra web; A09 xác nhận nội dung prompt injection trong knowledge base được tách vào `untrusted_text` và không được thực thi.
- AI/công cụ đã dùng và cách kiểm tra: Dùng Codex để đọc source, kiểm tra cấu trúc eval và phân tích run JSON; dùng `run_eval.py`, `scripts/preflight_provider.py` và tool result trong run để kiểm tra. Đã kiểm tra ticket tạo từ A03 là ticket local mock, không chứa secret và bị `/tickets/` trong `.gitignore` chặn khỏi Git. Các kết luận chỉ dùng run OpenAI adversarial đủ 12/12 case đo được; các run có lỗi quota Gemini được ghi nhận là lỗi provider, không tính là fail của agent.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
