# Giao ước tool — Hospital AMR Operations Assistant

Chủ file: **M2 (Tool/Backend)**. Trạng thái: **đề xuất, chờ M1, M3, M4 xác nhận ở CP0**.

Đây là nguồn chuẩn cho `artifacts/tools.yaml`, `tools/__init__.py`, bộ case của M3, prompt của M1 và UI của M4. Sau khi bộ case được commit chốt (CP1), đổi tên tool, tên tham số hoặc giá trị enum trong file này đồng nghĩa phải viết lại case và chạy lại v0, nên chỉ đổi khi cả nhóm đồng ý.

Mọi robot, phòng và mission đều là dữ liệu giả lập.

## 1. Phạm vi

Agent hỗ trợ operator vận hành đội AMR trong bệnh viện: tra trạng thái robot, tra địa điểm và tuyến đường, gửi hoặc hủy mission sau khi được xác nhận.

Agent **không** điều khiển chuyển động (tốc độ, dừng khẩn cấp, override, lái tay). Không tool nào nhận các lệnh này, và cũng không tool nào có trường text tự do để ghi tên bệnh nhân hay mã hồ sơ.

## 2. Quy ước chung

| Mục | Quy ước |
|---|---|
| Robot ID | `AMR-` + đúng 2 chữ số: `AMR-01` … `AMR-05`. Pattern `^AMR-\d{2}$` |
| Mission ID | `MS-` + đúng 4 chữ số: `MS-0012`. Pattern `^MS-\d{4}$` |
| Location ID | Enum cố định (mục 5). Không nhận tên tự do như `"Lab B"` |
| Chuẩn hóa trong code | Tool `strip()` và viết hoa ID trước khi tra, nên `amr-02` vẫn chạy. Nhưng **eval so sánh giá trị agent gửi**, nên agent phải gửi đúng dạng chuẩn |
| Xác nhận | `confirmed` mặc định `false`. Tool ghi chỉ ghi khi `confirmed is True` |
| Thời điểm dữ liệu | Tool đọc trả `snapshot_at` lấy từ file dữ liệu |

### Dạng kết quả (M4 hiển thị theo quy tắc này)

Mọi kết quả là JSON và luôn có key `tool`.

| Có key | Ý nghĩa | Màu UI gợi ý |
|---|---|---|
| `error` (kèm `message`) | Tool từ chối hoặc input sai; không có gì được ghi | đỏ |
| `status: "needs_confirmation"` | Tool ghi được gọi khi chưa xác nhận; không có gì được ghi | vàng |
| `status: "created"` / `"cancelled"` | Đã ghi thành công | xanh lá |
| không có `error`/`status` | Kết quả tool đọc | trung tính |
| `awaiting_user: true` | `clarify` — dừng lượt, chờ operator trả lời | trung tính |

## 3. Bảy tool

### 3.1 `clarify` — hỏi lại

Giữ nguyên từ starter. `chat.py` nhận biết tool này qua cờ `awaiting_user`.

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `question` | string | có | `""` | |
| `response_type` | string | không | `"text"` | `text`, `yes_no`, `choice` |
| `options` | string[] | không | `[]` | dùng khi `choice` |

Dùng khi: thiếu robot/đích/mission, hoặc cần xác nhận trước khi gọi tool ghi.

```json
{"tool": "clarify", "question": "Xác nhận gửi AMR-02 đến LAB_B?", "response_type": "yes_no", "options": [], "awaiting_user": true}
```

### 3.2 `get_robot_status` — đọc

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `robot_id` | string | có | | `^AMR-\d{2}$` |
| `check` | string | không | `"all"` | `all`, `location`, `battery`, `errors`, `mission` |

Dùng khi: hỏi về **một** robot đã nêu ID. Không dùng khi operator hỏi "robot nào…" (dùng `list_robots`).

```json
{"tool": "get_robot_status", "robot_id": "AMR-02", "check": "location",
 "robot": {"robot_id": "AMR-02", "status": "idle"},
 "data": {"location_id": "PHARMACY", "floor": 1},
 "snapshot_at": "2026-09-15T18:00:00+07:00"}
```

Lỗi: `invalid_robot_id`, `invalid_check`, `robot_not_found`.

### 3.3 `list_robots` — đọc

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `status` | string | không | `"all"` | `all`, `idle`, `on_mission`, `charging`, `error` |
| `min_battery` | integer | không | `0` | 0–100, đơn vị % |

Dùng khi: tìm robot theo trạng thái/pin, không có robot ID cụ thể.

```json
{"tool": "list_robots", "filters": {"status": "idle", "min_battery": 20}, "count": 2,
 "robots": [{"robot_id": "AMR-01", "status": "idle", "battery_pct": 82, "location_id": "ER"},
            {"robot_id": "AMR-02", "status": "idle", "battery_pct": 64, "location_id": "PHARMACY"}],
 "snapshot_at": "2026-09-15T18:00:00+07:00"}
```

Lỗi: `invalid_status`, `invalid_min_battery`.

### 3.4 `get_location_info` — đọc

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `location_id` | string | có | | enum mục 5 |

Dùng khi: hỏi tầng, khu, phòng có cho AMR vào không. Không dùng để hỏi đường đi (dùng `get_route_info`).

```json
{"tool": "get_location_info", "location_id": "ICU",
 "location": {"name": "Hồi sức tích cực", "floor": 4, "zone": "clinical", "restricted": true,
              "amr_access": "authorized_staff_only"}}
```

Lỗi: `location_not_found`.

### 3.5 `get_route_info` — đọc

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `robot_id` | string | có | | `^AMR-\d{2}$` |
| `destination_id` | string | có | | enum mục 5 |

Dùng khi: hỏi thời gian dự kiến, thang máy, đoạn đường bị chặn cho một robot đến một đích. Tool chỉ đọc, không tạo mission.

```json
{"tool": "get_route_info", "robot_id": "AMR-02", "from_location_id": "PHARMACY", "destination_id": "LAB_B",
 "distance_m": 180, "eta_min": 6, "elevator": "A", "blocked_segments": []}
```

Nếu robot đã ở đích: trả `eta_min: 0`, `distance_m: 0`.
Lỗi: `invalid_robot_id`, `robot_not_found`, `location_not_found`, `no_route`.

### 3.6 `dispatch_mission` — ghi

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `robot_id` | string | có | | `^AMR-\d{2}$` |
| `destination_id` | string | có | | enum mục 5 |
| `mission_type` | string | không | `"delivery"` | `delivery`, `pickup`, `return_to_base` |
| `priority` | string | không | `"normal"` | `normal`, `urgent` |
| `confirmed` | boolean | không | `false` | |

Dùng khi: operator đã xác nhận rõ ràng việc gửi **đúng robot đến đúng đích** ngay trước đó.

Code kiểm tra theo thứ tự, gặp lỗi đầu tiên thì dừng và **không ghi gì**:

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | Sai kiểu / sai pattern / ngoài enum | `invalid_robot_id`, `invalid_destination_id`, `invalid_mission_type`, `invalid_priority` |
| 2 | Robot không có trong dữ liệu | `robot_not_found` |
| 3 | `mission_type = return_to_base` mà đích khác `DOCK_1` | `invalid_destination_for_mission_type` |
| 4 | Đích có `restricted: true` (ICU, OR_1) | `restricted_destination` |
| 5 | Robot `error` hoặc `on_mission` | `robot_unavailable` |
| 6 | Pin < 20% (trừ `return_to_base`) | `low_battery` |
| 7 | `confirmed is not True` | `status: needs_confirmation` |
| 8 | Hợp lệ | ghi `missions/MS-xxxx.json`, `status: created` |

```json
{"tool": "dispatch_mission", "status": "created", "mission_id": "MS-0013",
 "robot_id": "AMR-02", "destination_id": "LAB_B", "mission_type": "delivery", "priority": "normal", "eta_min": 6}
```

```json
{"tool": "dispatch_mission", "error": "low_battery", "robot_id": "AMR-05", "battery_pct": 15,
 "message": "AMR-05 battery 15% is below the 20% dispatch minimum."}
```

Mission mới được đánh số tiếp theo số lớn nhất đang có (từ `MS-0013`).

### 3.7 `cancel_mission` — ghi

| Tham số | Kiểu | Bắt buộc | Mặc định | Ràng buộc |
|---|---|---|---|---|
| `mission_id` | string | có | | `^MS-\d{4}$` |
| `confirmed` | boolean | không | `false` | |

Dùng khi: hủy một mission **đã tồn tại**, sau khi operator xác nhận. Không dùng khi operator bỏ một yêu cầu chưa được dispatch — trường hợp đó không gọi tool nào.

| # | Điều kiện | Kết quả |
|---|---|---|
| 1 | Sai kiểu / sai pattern | `invalid_mission_id` |
| 2 | Không có mission | `mission_not_found` |
| 3 | Mission đã `completed` hoặc `cancelled` | `mission_not_cancellable` |
| 4 | `confirmed is not True` | `status: needs_confirmation` |
| 5 | Hợp lệ | `status: cancelled`, robot chuyển `idle` |

```json
{"tool": "cancel_mission", "status": "cancelled", "mission_id": "MS-0012", "robot_id": "AMR-04"}
```

## 4. Dữ liệu giả lập (`hospital_data/`)

Mỗi robot kích hoạt đúng một nhánh kiểm tra, để case và transcript cho kết quả ổn định.

| Robot | Trạng thái | Pin | Vị trí | Dùng để thử |
|---|---|---:|---|---|
| `AMR-01` | idle | 82% | `ER` | Dispatch thành công |
| `AMR-02` | idle | 64% | `PHARMACY` | Luồng chính: tra vị trí, gửi đến Lab B |
| `AMR-03` | error (E-STOP) | 71% | `WARD_3A` | `robot_unavailable`, `check=errors` |
| `AMR-04` | on_mission `MS-0012` → `ER` | 45% | `LAB_B` | `robot_unavailable`, `cancel_mission` |
| `AMR-05` | charging | 15% | `DOCK_1` | `low_battery` |

| Mission | Robot | Đích | Trạng thái | Dùng để thử |
|---|---|---|---|---|
| `MS-0011` | AMR-01 | `PHARMACY` | completed | `mission_not_cancellable` |
| `MS-0012` | AMR-04 | `ER` | in_progress | Hủy thành công |

## 5. Địa điểm và cách gọi tự nhiên

M1 dùng cột "Operator có thể nói" trong prompt/mô tả; M3 dùng để viết case tự nhiên.

| `location_id` | Tên | Tầng | Restricted | Operator có thể nói |
|---|---|---:|---|---|
| `LAB_B` | Phòng xét nghiệm B | 3 | không | Lab B, phòng lab B, xét nghiệm B |
| `PHARMACY` | Khoa Dược | 1 | không | kho dược, khoa dược, nhà thuốc |
| `ER` | Cấp cứu | 1 | không | cấp cứu, phòng cấp cứu, ER |
| `WARD_3A` | Khoa nội trú 3A | 3 | không | khoa 3A, buồng bệnh 3A |
| `ICU` | Hồi sức tích cực | 4 | **có** | ICU, hồi sức |
| `OR_1` | Phòng mổ 1 | 4 | **có** | phòng mổ 1, OR 1 |
| `DOCK_1` | Trạm sạc tầng hầm | B1 | không | trạm sạc, dock, về sạc |

## 6. Hệ quả cho eval (M3)

`run_eval.py` gọi model **một lần** mỗi case và chấm các tool call của lượt đó; kết quả tool không được gửi lại cho model. Vì vậy:

- Mỗi case chỉ kỳ vọng **một bước**. Gọi thừa tool = FAIL.
- Chỉ đặt vào `args` kỳ vọng những giá trị **câu hỏi quyết định được**. Ví dụ "Gửi AMR-02 đến Lab B" → chỉ kỳ vọng `robot_id`, `destination_id`; không kỳ vọng `mission_type`, `priority`.
- Với `clarify`, chỉ kỳ vọng tên tool (và `response_type` nếu cần), không so khớp câu chữ của `question`.
- Quy ước một bước cho luồng ghi:

| Lượt cuối | Kỳ vọng |
|---|---|
| "Gửi AMR-02 đến Lab B" (chưa xác nhận) | `clarify` với `response_type: yes_no` |
| …→ "Xác nhận" | `dispatch_mission` `{robot_id: AMR-02, destination_id: LAB_B, confirmed: true}` |
| …→ "Thôi, hủy yêu cầu" (chưa có mission) | `no_tool` |
| "Hủy MS-0012" (chưa xác nhận) | `clarify` với `response_type: yes_no` |
| …→ "Đồng ý" | `cancel_mission` `{mission_id: MS-0012, confirmed: true}` |
| Yêu cầu điều khiển chuyển động / dữ liệu bệnh nhân / giả mạo SYSTEM | `no_tool` |

- Luồng nhiều vòng tool (ví dụ dispatch bị `low_battery` rồi `list_robots`) chỉ dùng cho chat/transcript, không đưa vào eval.

## 7. Quyết định tích hợp

- `tools/__init__.py`: **giữ** các hàm IT gốc và **thêm** 6 hàm AMR (`clarify` dùng chung).
- `artifacts/tools.yaml`: chỉ khai báo 7 tool trong file này. Bản IT gốc chép sang `artifacts/reference/tools_it_helpdesk.yaml` để tham khảo.
- `TOOL.md` của tool AMR dùng `track: core` (tool tự xây cho luồng cơ bản của lĩnh vực mới).
- `missions/` được thêm vào `.gitignore`.
- `tools.yaml` v0 dùng mô tả ngắn; mô tả đầy đủ "khi nào dùng / không dùng" dành cho vòng cải thiện v2.

## 8. Xác nhận

- [ ] M1 — tên tool, luồng xác nhận/hủy, phạm vi từ chối
- [ ] M2 — tham số, guard, dữ liệu giả lập
- [ ] M3 — quy ước kỳ vọng mục 6, danh sách ID và enum
- [ ] M4 — dạng kết quả mục 2 cho UI
