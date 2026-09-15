# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Trương Hoàng Thanh An
- Người đại diện / MSSV: Trương Hoàng Thanh An / 2A202602574
- Tên repo: `K4-L3-DAY04-TruongHoangThanhAn-2A202602574-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: https://github.com/MinhTienNguyen05/K4-L3-DAY04-TruongHoangThanhAn-2A202602574-PromptEngineeringToolCalling, branch main
- Deadline áp dụng và link thông báo đổi hạn nếu có: 23:59 ngày học, Asia/Ho_Chi_Minh (UTC+07:00)

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Trương Hoàng Thanh An | 2A202602574 | MinhTienNguyen05 | Safety & Eval Engineer: Viết 10 eval cases, phân tích adversarial, xây bonus tool check_asset_warranty | eval_group.json, check_asset_warranty/, adversarial_safety_analysis.md |

## Nhận xét chung

- **Kết quả và bằng chứng:**
  - Hoàn thành 10 eval cases cho nhóm (5 single-turn + 5 multi-turn) trong `eval_group.json`
  - Xây dựng bonus tool `check_asset_warranty` để kiểm tra bảo hành thiết bị
  - Viết phân tích safety cho 12 adversarial cases trong `adversarial_safety_analysis.md`
  - Tích hợp bonus tool vào tools registry và tools.yaml
  - Chạy eval base với custom provider (Qwen): 20/30 cases PASS (66.67%)

- **Thay đổi hiệu quả nhất:**
  - Tạo bonus tool `check_asset_warranty` cung cấp chức năng mới ngoài luồng cơ bản
  - 10 eval cases bao phủ đủ các failure_type: wrong_tool, wrong_arg_value, missing_info, out_of_scope, unnecessary_tool, wrong_boundary

- **Giới hạn còn lại:**
  - Chưa chạy eval group cases và adversarial với custom provider (do thời gian)
  - Cần chạy thêm transcript và demo để hoàn thiện

- **Cách phân công và tích hợp:**
  - Thành viên đơn lẻ: Trương Hoàng Thanh An
  - Phân công: Safety & Eval Dataset & Bonus Tool Engineer

## INDIVIDUAL

### Trương Hoàng Thanh An — 2A202602574

- **Phần việc và file/commit/PR:**
  - Tạo `starter_v0/data/eval_group.json` - 10 eval cases (5 single-turn + 5 multi-turn)
  - Xây dựng `starter_v0/tools/check_asset_warranty/` - Bonus tool kiểm tra bảo hành (TOOL.md, __init__.py, tool.py)
  - Tạo `starter_v0/data/eval_bonus_warranty.json` - 5 test cases cho bonus tool
  - Viết `starter_v0/analysis/adversarial_safety_analysis.md` - Phân tích 12 adversarial cases
  - Cập nhật `starter_v0/tools/__init__.py` - Đăng ký bonus tool
  - Cập nhật `starter_v0/artifacts/tools.yaml` - Khai báo bonus tool
  - Tạo `starter_v0/providers/custom_provider.py` - Provider cho Qwen/Moonshot
  - Tạo `starter_v0/runs/v0_B_base_custom_20260915T192321182963.json` - Run eval base với Qwen

- **Quyết định, khó khăn và cách xử lý:**
  - Khó khăn: Gemini API key bị PERMISSION_DENIED và rate limit
  - Quyết định: Tạo custom provider cho Qwen sử dụng OpenAI-compatible API
  - Cách xử lý: Dùng `OPENAI_API_KEY` + `OPENAI_BASE_URL` + `MODEL=qwen3.7-flash`

- **Điều đã học:**
  - Hiểu cách thiết kế eval cases cho agent với nhiều failure types khác nhau
  - Học cách xây dựng bonus tool mới theo contract đúng
  - Nắm vững các attack vectors trong adversarial testing (prompt injection, role spoofing, data exfiltration)
  - Hiểu cách tạo custom provider cho OpenAI-compatible API

- **AI/công cụ đã dùng và cách kiểm tra:**
  - Claude Code (current) - Để viết code và phân tích
  - Cách kiểm tra: Chạy `python3 -c "from tools.check_asset_warranty.tool import check_asset_warranty; print(check_asset_warranty('LT-204'))"`

- **Thời điểm đã tự nộp URL repo chung trên VLearn:**
  - Chưa nộp - cần commit tất cả file và push lên GitHub trước
