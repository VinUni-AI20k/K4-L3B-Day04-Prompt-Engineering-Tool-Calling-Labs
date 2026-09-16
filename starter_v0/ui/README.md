# UI chat — Day04 Helpdesk Agent

Giao diện web local, chỉ dùng thư viện chuẩn của Python (không thêm dependency mới). Tái sử dụng nguyên logic gọi model/tool trong `chat.py` — không sửa `agent.py`, `run_eval.py`, `tools/`, `providers/`.

## Chạy

```powershell
cd starter_v0
python ui/server.py --provider anthropic --version v0
```

Mở trình duyệt tại `http://127.0.0.1:8765`.

Các tham số khác (mặc định giống `chat.py`):

```powershell
python ui/server.py --provider anthropic --model claude-3-5-sonnet-20241022 --version v1 --port 8080 --history-window 5 --max-tool-rounds 4
```

- `--version`: nhãn version hiển thị trong UI và ghi vào transcript (v0, v1, v2, v3...). Đổi nhãn này mỗi khi bắt đầu test một version mới.
- `artifacts/system_prompt.md` và `artifacts/tools.yaml` được đọc **một lần lúc khởi động** — sau khi sửa prompt/tool cho version tiếp theo, phải dừng (Ctrl+C) và chạy lại server để nạp bản mới.

## Các phần trong UI

- **Sidebar**: version hiện tại, artifact hash, provider/model, transcript đang ghi, danh sách tool (core/optional) lấy trực tiếp từ `tools.yaml`.
- **Tab "Chat trực tiếp"**: chat với agent; mỗi câu trả lời hiện kèm tool call (tên + args) và tool result/error thực tế theo từng round, cùng trạng thái lượt (`answered` / `waiting_for_user` / `provider_error` / `max_tool_rounds`). Mỗi tin nhắn tự ghi vào `starter_v0/transcripts/`.
- **Tab "Transcript đã lưu"**: duyệt lại mọi transcript đã ghi (kể cả file mẫu trong `samples/transcripts/`), nhóm theo version, xem lại toàn bộ hội thoại + tool trace.
- **Tab "Kết quả Eval (v0–v3)"**: đọc trực tiếp `starter_v0/runs/*.json` do `run_eval.py` tạo ra, hiển thị summary theo version (case accuracy, tool routing, argument accuracy, provider_error_cases) và bảng pass/fail từng case — dùng để so sánh trước/sau giữa các version. Một run chỉ được đánh dấu "hợp lệ" khi `provider_error_cases == 0` và `measured_cases == total_cases`, đúng điều kiện rubric.

## Ghi chú

- UI chỉ giữ 1 phiên hội thoại tại một thời điểm (in-memory, có lock) — đúng với cách `chat.py` hoạt động, phù hợp cho demo trực tiếp trên lớp.
- Lỗi provider (rate limit, sai key...) không bị nuốt — trả về JSON `provider_error` kèm message, hiển thị ngay trong khung chat.
