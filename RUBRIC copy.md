# Rubric Day04 — Tổng 100 điểm

**Phần chung 90 điểm + mở rộng (bonus) tối đa 10 điểm = 100 điểm.** Không làm mở rộng thì tối đa 90 điểm.

| Tiêu chí | Điểm | Bằng chứng cần có | Không tính điểm khi |
|---|---:|---|---|
| Prompt và mô tả công cụ | 20 | Quy tắc/mô tả rõ, khớp registry và run | Tên hoặc tham số không khớp, không có run |
| v0 đến v3 | 20 | v0, v1, v2, v3; giả thuyết, thay đổi, run, so sánh, version log | Chỉ đổi nhãn, thiếu run hoặc run lỗi provider |
| 10 case nhóm | 10 | Đúng 5 một lượt + 5 nhiều lượt, có kỳ vọng, run và phân tích | Sao chép bộ có sẵn, thiếu cấu trúc hoặc run |
| Hội thoại và an toàn | 15 | Run 12 case an toàn, phân tích 3 case, minh chứng hỏi lại/xác nhận/hủy/dữ liệu | Chỉ ghi PASS/FAIL, tự đoán mã hoặc gửi dữ liệu bị cấm |
| UI và transcript | 10 | UI chạy được, hiện tool, input, kết quả/lỗi, phiên bản và transcript | Chỉ có ảnh hoặc che lỗi công cụ |
| Report | 10 | Cách chạy, trước/sau, giới hạn và liên kết evidence | Nhận xét không có file hoặc commit đối chiếu |
| Làm nhóm | 5 | TEAM, commit kỹ thuật và INDIVIDUAL của từng người | Chỉ ghi tên hoặc tự đánh giá thay cho bằng chứng |

Run dùng làm bằng chứng phải có `provider_error_cases == 0` và `measured_cases == total_cases`. Một kết quả chưa tăng điểm vẫn được tính quy trình khi nhóm chạy thật, phân tích đúng và ghi trung thực.

Áp dụng cùng tiêu chí cho mọi lĩnh vực. Bộ cơ bản 30 câu và bộ an toàn 12 câu là bộ IT có sẵn hoặc bộ tương ứng của nhóm theo README. Việc tự xây công cụ để phục vụ luồng cơ bản của lĩnh vực mới được chấm trong phần chung.

## Bonus kỹ thuật

10 điểm này nằm trong thang 100, dành cho **một chức năng mới ngoài luồng cơ bản đã chốt của nhóm**: 3 điểm hữu ích, 2 điểm tích hợp, 3 điểm kiểm thử, 2 điểm an toàn/demo. Chọn lĩnh vực khác, đổi tên công cụ hoặc dùng nguyên công cụ có sẵn không tự được điểm. Chức năng mở rộng cần dữ liệu, code tích hợp, case kiểm thử và demo. Áp dụng như nhau cho mọi lĩnh vực.

Điểm lab giữ trong thang 0–100: `max(0, min(100, điểm bắt buộc + bonus) - điểm trừ muộn)`. Mức trừ muộn theo thông báo Keycoach; không tự đặt con số.
