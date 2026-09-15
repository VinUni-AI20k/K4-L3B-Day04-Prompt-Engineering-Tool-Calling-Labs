# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình[cite: 31].

## Thông tin bài nộp[cite: 31]

- Tên nhóm: Phan-Danh-Dat-2A202602627[cite: 31]
- Người đại diện: Phan Danh Đạt
- Tên repo: `K4-L3-DAY04-Phan-Danh-Dat-2A202602627-PromptEngineeringToolCalling`[cite: 31]
- URL repo, nhánh nộp, commit chốt: https://github.com/VinUni-AI20k/K4-L3-DAY04-Phan-Danh-Dat-2A202602627-PromptEngineeringToolCalling, nhánh `main`
- Deadline áp dụng và link thông báo đổi hạn nếu có: 23:59 ngày 15/09/2026 (theo quy định lab)

## Thành viên[cite: 31]

| Họ và tên / Username | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|
| Phan Danh Đạt | datphan-dev | Trưởng nhóm; kiến trúc system prompt, phân tích lỗi v0–v5, viết bộ case nhóm và tổng hợp report | `starter_v0/artifacts/system_prompt.md`, `version_log.csv`, `data/eval_group.json`, `artifacts/REPORT.md` |
| hoangvanson_02375 | hoangvanson_02375 | Thành viên; thiết kế kịch bản test case đơn lượt (`G01`–`G05`), hỗ trợ rà soát schema `tools.yaml` | `data/eval_group.json`, `starter_v0/artifacts/tools.yaml` |
| thong | thong | Thành viên; xây dựng kịch bản multi-turn test case (`M01`–`M05`), kiểm thử intent switching và cancellation | `data/eval_group.json`, `runs/` |
| khanh2a202602627 | khanh2a202602627 | Thành viên; chạy kiểm thử an toàn (adversarial / safety eval), phân tích lỗ hổng prompt injection và rò rỉ dữ liệu | `data/eval_adversarial.json`, `starter_v0/artifacts/REPORT.md` |
| anh | anh | Thành viên; chạy kiểm thử giao diện người dùng (UI), ghi nhận log và xuất transcript hội thoại mẫu | `transcripts/`, `starter_v0/artifacts/REPORT.md` |

## Nhận xét chung[cite: 31]

- Kết quả và bằng chứng[cite: 31]:
  - Đã thực hiện trọn vẹn chu trình cải tiến qua các phiên bản từ v0 đến v5 trên bộ kiểm thử chuẩn (`eval_base.json`), nâng case accuracy từ 70.0% lên 100% (30/30 passed, `provider_error_cases == 0`)[cite: 1, 23].
  - Xây dựng thành công bộ 10 test case chuyên biệt của nhóm (`eval_group.json`) bao gồm 5 câu single-turn và 5 câu multi-turn, bao quát các tình huống kiểm tra phần cứng, tra cứu trạng thái, huỷ thao tác và cập nhật payload[cite: 8, 29].
  - Mọi thay đổi và telemetry được ghi vết đầy đủ tại `version_log.csv` và các file run JSON tương ứng trong thư mục `runs/`[cite: 10, 14].
- Thay đổi hiệu quả nhất[cite: 31]:
  - Thiết lập ranh giới an toàn (Confirmation Boundary) cho write action: ngăn chặn tuyệt đối việc tự ý gọi `create_ticket` ở lượt đầu hoặc khi payload thay đổi, bắt buộc gọi duy nhất `clarify(response_type="yes_no")`[cite: 1, 27].
  - Chuẩn hoá cơ chế trích xuất thực thể: chặn model tự đoán danh từ chung ("laptop", "Sales") làm ID và nhận diện đúng mã định danh thực tế (`LT-xxx`, `EMP-xxx`)[cite: 1, 27].
  - Ánh xạ rõ ràng enum `category` cho `search_kb` (`email`, `wifi`, `vpn`, `account`, `printing`)[cite: 27].
- Giới hạn còn lại[cite: 31]:
  - Vẫn cần theo dõi độ trễ API khi các chuỗi hội thoại kéo dài qua nhiều lượt liên tiếp.
  - Phụ thuộc vào tính ổn định của LLM khi người dùng diễn đạt nhiều ý định phức tạp trong một câu duy nhất.
- Cách phân công và tích hợp[cite: 31]:
  - Nhóm trưởng điều phối kiến trúc prompt và luồng đánh giá tự động. Các thành viên đảm nhiệm từng mảng độc lập (single-turn, multi-turn, adversarial testing và UI transcript), sau đó tích hợp tập trung vào repo và đối chiếu chéo kết quả test run[cite: 10, 11].

## INDIVIDUAL[cite: 31]

### Phan Danh Đạt

- Phần việc và file/commit/PR:
  - Phân tích telemetry lỗi v0, thiết kế cấu trúc prompt và bổ sung các guardrails an toàn vào `starter_v0/artifacts/system_prompt.md`.
  - Thực hiện chạy và kiểm định các vòng lặp v0, v1, v2, v3, v4, v5, ghi nhận telemetry và phân tích sai lệch vào `version_log.csv`[cite: 1, 10, 19, 20, 21, 22, 23].
  - Đồng bộ schema cho bộ test runner, cấu hình `eval_group.json` và tổng hợp tài liệu `artifacts/REPORT.md`, `TEAM.md`[cite: 10, 29, 31].
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Khi cấm model dùng từ "laptop" làm `asset_id`, model phản ứng thái quá bằng cách hỏi lại mã máy ngay cả khi người dùng đã cung cấp mã hợp lệ dạng "laptop LT-204" (ở ca `H02`)[cite: 6, 7]. *Cách xử lý*: Tách rõ quy tắc: nếu chuỗi chứa mã máy thực tế (`LT-xxx`) thì trích xuất ngay, chỉ gọi `clarify` khi hoàn toàn không có mã định danh[cite: 7].
- Điều đã học:
  - Hiểu sâu về Function Calling trong LLM: prompt phải phân định ranh giới an toàn (boundary) rõ ràng cho các tác vụ ghi dữ liệu nhạy cảm[cite: 1, 27].
  - Nắm vững kỹ thuật State Tracking và Recency Rule trong xử lý hội thoại đa lượt[cite: 27].
- AI/công cụ đã dùng và cách kiểm tra:
  - Sử dụng Gemini hỗ trợ phân tích mismatch từ file log JSON; kiểm tra độc lập bằng cách chạy `run_eval.py` trên môi trường PowerShell/Python cục bộ[cite: 10].
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã nộp URL repo lên hệ thống VLearn trước deadline quy định[cite: 31].

### hoangvanson_02375

- Phần việc và file/commit/PR:
  - Soạn thảo và kiểm thử 5 test case single-turn (`G01`–`G05`) trong `data/eval_group.json`[cite: 8, 29].
  - Rà soát các tham số và kiểu dữ liệu trong `starter_v0/artifacts/tools.yaml` để đảm bảo tương thích với schema[cite: 9].
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Ca `G02` bị model gọi tool `inspect_device` tới 2 lần do câu lệnh ban đầu yêu cầu kiểm tra cả "hardware and battery"[cite: 30]. *Cách xử lý*: Điều chỉnh prompt và câu input tinh gọn, làm rõ phạm vi `check="hardware"` để model kích hoạt đúng 1 function call[cite: 9, 30].
- Điều đã học:
  - Kỹ thuật thiết kế query đơn nghĩa nhằm tránh hiện tượng multi-call ngoài ý muốn của mô hình[cite: 30].
- AI/công cụ đã dùng và cách kiểm tra:
  - Dùng AI hỗ trợ viết test case; kiểm tra bằng lệnh chạy eval chuyên biệt cho nhóm single-turn.
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã nộp URL repo lên hệ thống VLearn trước deadline quy định[cite: 31].

### thong

- Phần việc và file/commit/PR:
  - Thiết kế và chuẩn hóa 5 kịch bản hội thoại đa lượt (`M01`–`M05`) trong `data/eval_group.json`[cite: 8, 29].
  - Phân tích các ca kiểm thử liên quan đến Action Cancellation (`M03`) và Switching Intent (`M05`)[cite: 24, 29].
- Quyết định, khó khăn và cách xử lý:
  - *Khó khăn*: Runner ban đầu không kích hoạt cơ chế multi-turn khiến model nhận input mảng và trả về câu chào mặc định[cite: 28, 30]. *Cách xử lý*: Cấu hình trường `"is_multiturn": true` và chuẩn hóa tiền tố ID để runner nạp đúng luồng đàm thoại[cite: 29].
- Điều đã học:
  - Hiểu cách thức test runner mô phỏng hội thoại đa lượt (turn-by-turn) và cách LLM duy trì ngữ cảnh qua lịch sử tin nhắn.
- AI/công cụ đã dùng và cách kiểm tra:
  - Dùng AI phân tích hành vi context leak; kiểm tra thực tế bằng log run JSON của bộ `eval_group.json`[cite: 24, 30].
- Thời điểm đã tự nộp URL repo chung trên VLearn:
  - Đã nộp URL repo lên hệ thống VLearn trước deadline quy định[cite: 31].

### khanh2a202602689

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:
