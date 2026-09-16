# TEAM — Day04, K4-L3B

## Thông tin bài nộp

- Tên nhóm: T084
- Người đại diện / MSSV: Phạm Anh Minh / 2A202603009
- Tên repo: K4-L3-DAY04-PhamAnhMinh-2A202603009-PromptEngineeringToolCalling
- URL repo, nhánh nộp, commit chốt: https://github.com/map1509/K4-L3-DAY04-PhamAnhMinh-2A202603009-PromptEngineeringToolCalling
- Deadline áp dụng và link thông báo đổi hạn nếu có: 16/09/2026 12pm

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Phạm Anh Minh | 2A202603009 | map1509 | Dẫn dắt nhóm, tổng hợp workflow, tối ưu prompt/tool, kiểm tra chạy eval và báo cáo | system_prompt.md, tools.yaml, REPORT.md
| Tô Anh Đức | 2A202602639 | AnhDuc0712 | Thiết kế baseline ban đầu, góp ý cho tool routing và so sánh phiên bản v0-v3 | eval_base.json,  __init__.py, JSON trong runs, systemprompt.md|
| Vũ Bá Anh | 2A202602893 | anhvb702 | Phụ trách chỉnh sửa model behavior qua các phiên bản và đánh giá lỗi từ run | tool.py, systemprompt.md |
| Hồ Hoàng Phương Anh | 2A202602460 | abbeyIsMe | Hỗ trợ sản phẩm, tài liệu nhóm, chuẩn hóa TEAM.md và ghi chú tiến độ | REPORT.md, SUBMISSION.md, check point RULES.md, RUBRIC.md |

## Nhận xét chung

- Kết quả và bằng chứng: Đã test, chạy baseline và các phiên bản cải tiến, xem lại dữ liệu, lỗi và phản hồi tool call để so sánh hiệu quả trước/sau. Xem trong các run JSON, `version_log.csv` và `starter_v0/artifacts/REPORT.md`
- Thay đổi hiệu quả nhất: Việc cải thiện `system_prompt.md` và mô tả tool trong `tools.yaml` giúp agent lựa chọn đúng tool, yêu cầu thông tin còn thiếu rõ ràng hơn và giảm các lỗi liên quan đến sai input hoặc thiếu xác nhận trong hội thoại nhiều lượt
- Giới hạn còn lại: Người dùng dùgn hội thoại dài vẫn cần được kiểm tra thêm ở mức độ phức tạp hoặc khi agent phải xử lý thông tin trong nội bộ công ty
- Cách phân công và tích hợp: Mỗi thành viên làm một phần trách nhiệm rõ ràng nhưng vẫn cùng review kết quả chung. Nền tảng làm việc là GitHub repo chung, các thay đổi được kiểm tra và thảo luận trước khi merge vào branch chính

## INDIVIDUAL

### Hồ Hoàng Phương Anh — 2A202602460

- Phần việc và file/commit/PR: Hỗ trợ sản phẩm, tài liệu nhóm, chuẩn hóa TEAM.md, REPORT.md, check các files đúng với yêu cầu và ghi chú tiến độ
- Quyết định, khó khăn và cách xử lý: Điêuf hướng để team không đi chệch khỏi mục tiêu 
- Điều đã học: Build 1 agent làm đúng phần việc, kiểm tra và cải tiến từng phiên bản
- AI/công trợ đã dùng và cách kiểm tra: Claude
- Thời điểm đã tự nộp URL repo chung trên VLearn: [15/9/2026 8:55pm]

### Phạm Anh Minh — 2A202603009

- Phần việc và file/commit/PR: Tối ưu prompt/tool, UX/UI design. Các file chính: system_prompt.md, tools.yaml, version_log.csv
- Quyết định, khó khăn và cách xử lý: Khó khăn chính: cân bằng giữa hỏi lại (clarify) và trải nghiệm người dùng; giải pháp: thêm ví dụ minh họa và rule trong system_prompt.md để buộc hỏi trường cần thiết
- Điều đã học: Kinh nghiệm thực tế về prompt engineering cho tool-calling, thiết kế schema tool hợp lý, và quy trình ghi evidence (runs/transcripts/version_log).
- AI/công trợ đã dùng và cách kiểm tra: Dùng provider để chạy eval openrouter
- Thời điểm đã tự nộp URL repo chung trên VLearn: [15/9/2026 8:55pm]

### Tô Anh Đức — 2A202602639

TỰ ĐIỀN NỐT HỘ C NHA MẤY BÉ

- Phần việc và file/commit/PR: starter_v0/data/eval_base.json, runs/v1_base.json
- Quyết định, khó khăn và cách xử lý:
- Điều đã học: 
- AI/công trợ đã dùng và cách kiểm tra: (ví dụ OpenAI/Claude + cách kiểm tra)
- Thời điểm đã tự nộp URL repo chung trên VLearn: [15/9/2026 8:55pm]

### Vũ Bá Anh — 2A202602893

- Phần việc và file/commit/PR: artifacts/tools.yaml, runs/v2_base.json
- Quyết định, khó khăn và cách xử lý: 
- Điều đã học: 
- AI/công trợ đã dùng và cách kiểm tra: Claude
- Thời điểm đã tự nộp URL repo chung trên VLearn: [15/9/2026 8:55pm]