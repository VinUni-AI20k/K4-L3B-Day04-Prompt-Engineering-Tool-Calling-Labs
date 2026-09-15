# Experiment & Prompt Lead — Nguyễn Hoàng Cường

## Trạng thái evidence

Đã tạo `.venv`, cài `requirements.txt` và tạo `.env` từ mẫu (file này được gitignore). Key hiện được cấu hình cho Gemini. Preflight `gemini-3.5-flash` và `gemini-3.5-flash-lite` đã trả structured tool call. Run v0 bằng model mặc định được lưu tại `runs/v0_B_base_gemini_20260915T185750558866.json`, nhưng **không hợp lệ làm baseline**: `total_cases=30`, `measured_cases=1`, `provider_error_cases=29`. Từ H02 trở đi API trả `429 RESOURCE_EXHAUSTED`. V0 chạy lại với `gemini-3.5-flash-lite` tại `runs/v0_B_base_gemini_20260915T190154823375.json` có `total_cases=30`, `measured_cases=0`, `provider_error_cases=30` (cùng lỗi 429). Model `gemini-2.5-flash-lite` trả 404 vì không còn khả dụng cho người dùng mới. Chưa có run v0/v1 hợp lệ và chưa có metric trước/sau. Version log ghi rõ hai run diagnostic không hợp lệ và v1 mới chuẩn bị.

Prompt gốc được lưu tại `system_prompt.v0.md`, SHA-256 `27467914BC4D93574EB1A418B77247C51682E04401C78FB4445C22B9019185A0`. Tool declaration chưa sửa, SHA-256 `D4848549884EB9613313A2A8DEC5FACA4E8299842790AC2D42A04195B4DA3198`.

## Giả thuyết v1 (chưa được kiểm chứng bằng run)

Prompt gốc chỉ nói chung rằng có thể dùng tool, không hướng dẫn chọn nhiều nguồn, dùng thông tin mới nhất hoặc xác nhận payload ticket. Bộ 30 case cố định cho thấy các tình huống cần nhiều call (H13, H15–H18), sửa/hủy nhiều lượt (M03, M07–M10), thiếu ID/môi trường (H10, H11, H19) và confirmation boundary (H12, M05, M09). Đây là **rủi ro thiết kế suy ra từ case**, không phải lỗi baseline quan sát từ trace. V1 bổ sung quy tắc routing, carry/correction/cancellation, clarify, và xác nhận ticket. Metric chính sẽ là `case_accuracy`; xem thêm `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`, `provider_error_cases`, `measured_cases` và kết quả thực thi của từng tool.

## Lệnh chạy khi đã có key

Điền key tại `starter_v0/.env` trên máy, không commit hoặc gửi key qua chat. Chạy trong `starter_v0`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider gemini --model gemini-3.5-flash-lite
.\.venv\Scripts\python.exe run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v0 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/system_prompt.v0.md
.\.venv\Scripts\python.exe run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v1 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/system_prompt.md
```

Chỉ sau khi hai run đạt `provider_error_cases == 0` và `measured_cases == total_cases`, đọc cả `tool_results`, phân tích các case FAIL từ trace, rồi điền số đo và đường dẫn run thật vào `version_log.csv`. Cùng provider, model, dataset và `tools.yaml` phải được giữ qua cả hai run.
