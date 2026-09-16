# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Soul
- Người đại diện / MSSV:
- Tên repo: `K4-L3-DAY04-Soul-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: <https://github.com/duanhap/K4-L3-DAY04-Soul-PromptEngineeringToolCalling>.
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Phùng Quốc Việt | [2A202602456] | PhungQuocViet |Kỹ sư Prompt Core: Khởi tạo repo/môi trường; tối ưu lặp `system_prompt.md` qua các phiên bản v0->v1->v2->v3 đạt 100% (30/30); thiết kế 10 test case nhóm `data/eval_group.json`; quản lý nhật ký `version_log.csv` và điều phối tích hợp git | `artifacts/system_prompt.md`<br>`data/eval_group.json`<br>`artifacts/version_log.csv`<br>`runs/v0_...` đến `v3_...`<br>Commits: v1, v2-v3, 10 testcase gr |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

Sao chép mục này cho từng thành viên.

### Phùng Quốc Việt — [2A202602456]

- Phần việc và file/commit/PR:
  - Khởi tạo môi trường ảo, cấu hình adapter provider OpenAI gpt-4o-mini và giải quyết xung đột thư viện.
  - Phụ trách chính kiến trúc prompt: xây dựng `artifacts/system_prompt.md`, phân tích failure trace từ v0 và lặp qua v1, v2, chốt v3 đạt 30/30 (100%).
  - Phối hợp tinh chỉnh schema `artifacts/tools.yaml` (đưa `response_type` vào `required`, phân định enum).
  - Thiết kế giải pháp phân định ranh giới Read Tools (thực thi ngay) vs Write Tools (bắt buộc xác nhận) và xử lý ngữ cảnh đa lượt (nhớ mã máy, cập nhật thông tin, hủy lệnh).
  - Quản lý nhật ký thử nghiệm `artifacts/version_log.csv`, dọn dẹp các run rác và đồng bộ bằng chứng lên branch `vietpq`.
- Quyết định, khó khăn và cách xử lý: Khắc phục lỗi rate limit 429 quota bằng cách chuyển sang OpenAI gpt-4o-mini để đảm bảo run sạch; thiết lập ranh giới Read/Write tool để vừa tránh over-clarify ở H06 vừa đảm bảo xác nhận ở H12; phân tách rõ mã máy và mã nhân viên để triệt tiêu lỗi đoán mò ID.
- Điều đã học: Nắm vững cơ chế Tool Calling của LLM, kỹ thuật Prompt Engineering có cấu trúc, phương pháp tối ưu lặp có đối chứng và kỹ năng điều phối dự án nhóm trên Git.
- AI/công cụ đã dùng và cách kiểm tra: Sử dụng trợ lý AI hỗ trợ gợi ý ý tưởng; luôn tự kiểm chứng bằng cách chạy thực tế `run_eval.py` trên môi trường thật để kiểm tra trace.
- Thời điểm đã tự nộp URL repo chung trên VLearn: [00:27 ngày 16/09/2026]
