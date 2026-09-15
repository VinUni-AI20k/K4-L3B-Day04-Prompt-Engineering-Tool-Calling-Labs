2. Định hình Đề tài & Bộ Test Case
 Chốt đề tài: Giữ IT Helpdesk hoặc đổi sang lĩnh vực khác (Du lịch, Bán hàng, Thư viện...).
 Nếu đổi lĩnh vực: Tạo bộ eval riêng (30 case cơ bản: 20 single-turn + 10 multi-turn; 12 case adversarial), chốt trước khi chạy v0.
 Viết case mở rộng cho nhóm: Hoàn thiện file data/eval_group.json với đúng 10 cases (5 single-turn + 5 multi-turn).
3. Chạy Thực Nghiệm & Tối Ưu (v0 → v3)
 Chạy Baseline (v0): py run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json (chưa sửa code/prompt).
 Phân tích lỗi v0: Đánh giá routing, args, missing info, multi-turn, safety.
 Tối ưu v1, v2, v3:
Đặt giả thuyết → Cải thiện artifacts/system_prompt.md hoặc artifacts/tools.yaml.
Chạy eval ghi log run JSON.
Cập nhật thông số, giả thuyết & kết quả so sánh vào version_log.csv.
Lưu ý: Chỉ công nhận run bằng chứng khi provider_error_cases == 0 và measured_cases == total_cases.
 Kiểm thử An toàn (Adversarial Suite): Chạy 12 case an toàn, phân tích ít nhất 3 case bị tấn công/rò rỉ dữ liệu.
4. Giao diện Chat UI & Transcripts
 Xây dựng Chat UI: Giao diện hiển thị rõ thông tin tool calls, arguments, kết quả/lỗi trả về, và artifact version hiện tại.
 Xuất Transcript: Đảm bảo có bằng chứng hội thoại thực tế cho các kịch bản: Normal, Missing info, Multi-turn, Action boundary (xác nhận/hủy).
5. Báo cáo & Nộp bài
 Hoàn thiện Report: Điền đầy đủ thông tin vào artifacts/REPORT.md (kiến trúc agent, bằng chứng qua từng version, safety review, thất bại & bài học).
 Đóng góp cá nhân: Cập nhật mục INDIVIDUAL của từng thành viên trong 

TEAM.md
.
 Clean-up check: Không commit .env, API key, .venv, dữ liệu thật hay file rác.
 Nộp VLearn: Mỗi thành viên tự nộp cùng URL Repo nhóm lên VLearn trước 23:59.
