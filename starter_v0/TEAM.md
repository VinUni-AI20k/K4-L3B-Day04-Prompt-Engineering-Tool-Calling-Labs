# Phân công Nhiệm vụ & Workflow Nhóm (IT Helpdesk Agent)

## 👥 Danh sách Phân công & Trạng thái

| Thành viên | Vai trò & Nhiệm vụ chính | Trạng thái | Sản phẩm bàn giao |
| :--- | :--- | :---: | :--- |
| **Hưng** | **Baseline & Eval infra (v0)**: Chạy preflight, chạy v0 gốc, đọc log/trace, phân loại lỗi và tổng hợp giả thuyết | **✅ HOÀN THÀNH** | HYPOTHESES_v0.md, 
uns/v0_B_base_gemini_*.json, ersion_log.csv (v0), Batch Rate-limit fix |
| **Hoàng Anh** | **Prompt & tool declaration (v1)**: Dựa trên giả thuyết của Hưng, chỉnh sửa rtifacts/system_prompt.md + rtifacts/tools.yaml, chạy v1, so sánh với v0, ghi ersion_log.csv | ⏳ TIẾP THEO | system_prompt.md, 	ools.yaml, 
uns/v1_*.json, update ersion_log.csv |
| **Thành** | **Tiếp tục lặp (v2, v3)**: Dựa trên v1, mỗi vòng 1 giả thuyết + 1 thay đổi chính, chạy lại eval, so sánh metric/trace, cập nhật version log | ⏳ TIẾP THEO | 
uns/v2_*.json, 
uns/v3_*.json, update ersion_log.csv |
| **Linh** | **Bộ case & An toàn**: Viết 10 case nhóm (5 đơn + 5 đa lượt) vào data/eval_group.json, chạy 12 case adversarial, phân tích ≥3 case an toàn (hỏi lại/xác nhận/hủy/dữ liệu) | ⏳ TIẾP THEO | data/eval_group.json, Báo cáo an toàn 12 cases |
| **Tuấn** | **UI, Transcript & Report**: Làm UI chat hiển thị tool call/input/kết quả-lỗi/version, lưu transcript, tổng hợp rtifacts/REPORT.md và điều phối TEAM.md | ⏳ TIẾP THEO | UI Chat (chat.py), rtifacts/REPORT.md, Push code origin Tuan |

---

## 🛠️ Hướng dẫn chuyển giao cho Hoàng Anh (Thực hiện v1)

Hoàng Anh sẽ sử dụng kết quả v0 từ Hưng để thực hiện các bước sau:

1. **Đọc giả thuyết v0**: Xem chi tiết 4 giả thuyết tại [HYPOTHESES_v0.md](./HYPOTHESES_v0.md).
2. **Chỉnh sửa File Artifacts**:
   - Sửa rtifacts/system_prompt.md: Bổ sung hướng dẫn bắt buộc dùng Native Function Call thay vì sinh text JSON (H07) và quy định quy trình hỏi xác nhận confirm_action trước khi tạo ticket (H12).
   - Sửa rtifacts/tools.yaml nếu cần làm rõ mô tả tham số/tools.
3. **Chạy Eval v1**:
   `ash
   python run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v1 --suite base --eval-cases data/eval_base.json
   `
4. **Cập nhật Version Log**:
   - So sánh metric case_accuracy giữa v0 và v1, sau đó thêm 1 dòng log vào rtifacts/version_log.csv.
