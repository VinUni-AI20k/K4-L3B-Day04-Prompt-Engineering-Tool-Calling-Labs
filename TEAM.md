# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Tứ Đại Bổ Túc
- Người đại diện / MSSV: Đỗ Nguyễn Ngọc Long
- Tên repo: `K4B-DAY4-TUDAIBOTUC`
- URL repo, nhánh nộp, commit chốt: https://github.com/ngoclongdo/K4B-DAY4-TUDAIBOTUC
- Deadline áp dụng và link thông báo đổi hạn nếu có: None

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
|Đỗ Nguyễn Ngọc Long |2A202602390 |https://github.com/ngoclongdo |Triển khai version 1 đên 3| `system_prompt.md`, `tools.yaml`, `version_log.csv` |
|Nguyễn Tuấn Anh |2A202602535 |https://github.com/Tuan2Anh |Triển khai 10 test cases | `eval_helpdesk_extension.json` |
|Cao Đức Anh |2A202602754 |https://github.com/CDanh0301 |Triển khai UI | `chat.py` |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Đỗ Nguyễn Ngọc Long — 2A202602390

- Phần việc và file/commit/PR: Thiết kế và tinh chỉnh system prompt, rules, và tools (v1, v2, v3). Cập nhật `system_prompt.md`, `tools.yaml`, `REPORT.md`, `version_log.csv`.
- Quyết định, khó khăn và cách xử lý: Khó khăn lớn nhất là model hay bị cuốn theo ngữ cảnh cũ (multi-turn) và tự động sinh ra thông tin giả. Cách xử lý là bổ sung các ràng buộc boundary rõ ràng về bảo mật và buộc xin xác nhận trước khi gọi external tool.
- Điều đã học: Hiểu sâu hơn về giới hạn của LLM khi làm tool calling, tầm quan trọng của việc kiểm soát luồng giao tiếp (dialogue state) qua system prompt.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng AI Agent hỗ trợ phân tích log và format báo cáo. Kiểm tra bằng cách chạy liên tục lệnh `run_eval.py`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Hôm nay.

### Cao Đức Anh — 2A202602754

- Phần việc và file/commit/PR: Thiết kế và triển khai giao diện trò chuyện trực tiếp (CLI) cùng vòng lặp xử lý tool (tool loop). Chịu trách nhiệm chính các file `chat.py` và `agent.py`.
- Quyết định, khó khăn và cách xử lý: Khó khăn lớn nhất là phải dừng vòng lặp suy luận khi model gọi tool `clarify` để chờ người dùng nhập thêm thông tin. Đã giải quyết bằng cách nhận diện cờ `awaiting_user` để tạm dừng, lấy input từ user và nhồi lại vào lịch sử.
- Điều đã học: Nắm bắt cách quản lý message history đa lượt (multi-turn), cách bóc tách tool calls JSON và thiết kế cơ chế lưu trữ transcript để truy vết lỗi dễ dàng.
- AI/công cụ đã dùng và cách kiểm tra: Dùng AI hỗ trợ viết hàm phân tích JSON và quản lý file. Kiểm thử trực tiếp trên terminal với lệnh `python chat.py`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Hôm nay.

### Nguyễn Tuấn Anh — 2A202602535

- Phần việc và file/commit/PR: Thiết kế và hoàn thiện 10 test cases nhóm (5 single-turn, 5 multi-turn) trong `starter_v0/data/eval_group.json`. Thực hiện chạy đánh giá v3 trên 3 bộ dataset (`eval_group.json`, `eval_helpdesk_extension.json`, `eval_adversarial.json`) với provider OpenRouter (`openai/gpt-oss-120b`), lưu trữ bằng chứng runs JSON. Hoàn thành toàn bộ nội dung phân tích test cases, adversarial safety review và technical reflection trong `starter_v0/artifacts/REPORT.md`.
- Quyết định, khó khăn và cách xử lý: Khó khăn trong việc thiết kế các ca kiểm thử đa lượt (multi-turn) thể hiện đúng ranh giới an toàn (như hủy yêu cầu tạo ticket, hoặc kiểm tra ranh giới xác nhận khi thay đổi payload). Đã xử lý bằng cách chuẩn hóa theo đúng cấu trúc của `run_eval.py` và kiểm thử xác thực thực tế.
- Điều đã học: Hiểu sâu về cách đánh giá định lượng năng lực tool-calling của LLM, sự khác biệt giữa điểm số tự động (automatic score) và an toàn thực tế (khi model chủ động từ chối bằng văn bản), và tầm quan trọng của việc kiểm soát ranh giới dữ liệu nhạy cảm.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng AI Agent hỗ trợ viết test cases và phân tích log. Kiểm tra kết quả trực tiếp bằng lệnh `python run_eval.py`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Hôm nay.
