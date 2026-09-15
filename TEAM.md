# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: KTD
- Người đại diện / MSSV: Trần Ngọc Khánh / 2A202602923
- Tên repo: `K4-L3-DAY04-KTD-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt:
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Trần Ngọc Khánh | 2A202602923 | trankhanh6162 | Prompt & Iteration Lead: chạy và phân tích v0-v3, cải thiện prompt/tool declarations, ghi version evidence | `abaa696`; `starter_v0/artifacts/{system_prompt.md,tools.yaml,version_log.csv,REPORT.md}`; `starter_v0/{runs,analysis}/` |
| Phùng Đức Đăng | 2A202602956 | dawn | UI, Bonus & Integration Lead: xây Web UI thời gian thực (hiển thị tool calls, args, results, artifact version), xây dựng và kiểm thử Technical Bonus Tool check_asset_warranty, tạo và đối soát 5 bộ transcripts thực tế, hoàn thiện Section A, B4, B5 trong REPORT.md | `starter_v0/ui.py`, `starter_v0/tools/check_asset_warranty/`, `starter_v0/scripts/test_bonus_tool.py`, `starter_v0/transcripts/`, `starter_v0/artifacts/REPORT.md` |

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

### Phùng Đức Đăng — 2A202602956

- Phần việc và file/commit/PR: UI, Bonus & Integration Lead. Xây dựng Web UI tương tác bằng Python Native HTTPServer (`starter_v0/ui.py`) hiển thị lịch sử hội thoại, artifact version, chi tiết tool call (tên, arguments, kết quả/lỗi), hỗ trợ nút kịch bản mẫu và xuất transcript JSON. Phát triển Technical Bonus Tool `check_asset_warranty` (`starter_v0/tools/check_asset_warranty/`) tra cứu hạn bảo hành phần cứng, phân loại trạng thái vòng đời thiết bị và cảnh báo SLA kèm bộ unit test 4/4 cases (`starter_v0/scripts/test_bonus_tool.py`). Chạy và lưu 5 bộ live transcript (`starter_v0/transcripts/`) cho v3. Tích hợp Header, Section A (A1-A4), Section B4, B5 trong `starter_v0/artifacts/REPORT.md` và hướng dẫn chạy UI trong `README.md`.
- Quyết định, khó khăn và cách xử lý: Quyết định quan trọng nhất là sử dụng `ThreadingHTTPServer` từ thư viện chuẩn Python (zero third-party dependency) thay vì framework ngoài, đảm bảo Web UI hoạt động ngay lập tức trong mọi môi trường. Khó khăn lớn nhất là giới hạn rate limit 429 từ cloud provider; tôi đã kết nối qua cổng 9Router cục bộ (`http://localhost:20128/v1`) với model `ag/gemini-3-flash`, hoàn thành thông suốt 5 kịch bản thực tế không lỗi.
- Điều đã học: Hiểu rõ cơ chế function calling và ranh giới an toàn (trust boundary). Khi thiết kế tool, việc tiền kiểm tra regex cho tham số đầu vào (`LT-xxx`, `PR-xxx`) là bắt buộc để ngăn chặn truy vấn rác, và các thao tác có tác động ghi dữ liệu (write actions) phải luôn có xác nhận rõ ràng trước khi thực thi.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng Antigravity và Python unittest. Kiểm tra độc lập: chạy bộ kiểm thử `starter_v0/scripts/test_bonus_tool.py` đạt 4/4 test cases pass, kiểm tra 5 tệp transcript trong `starter_v0/transcripts/` đảm bảo đúng schema và các bước gọi tool, khởi chạy Web UI qua `python ui.py --port 8080` và xác nhận giao diện hiển thị đúng phản hồi thời gian thực.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
