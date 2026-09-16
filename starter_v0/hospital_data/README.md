# Hospital AMR mock data

Dữ liệu giả lập cho Hospital AMR Operations Assistant. Không có robot, bệnh viện, nhân viên hay bệnh nhân thật. Quy ước ID, enum và trạng thái theo [docs/AMR_TOOL_CONTRACT.md](../docs/AMR_TOOL_CONTRACT.md).

| File | Nội dung | Tool đọc |
|---|---|---|
| `robots.json` | 5 robot: trạng thái, pin, vị trí, lỗi, mission hiện tại | `get_robot_status`, `list_robots`, `dispatch_mission` |
| `locations.json` | 7 địa điểm, cờ `restricted`, cách gọi tự nhiên | `get_location_info`, `dispatch_mission` |
| `routes.json` | 21 tuyến hai chiều, thang máy, đoạn đường bị chặn | `get_route_info`, `dispatch_mission` |
| `missions.json` | Mission có sẵn trước buổi demo | `cancel_mission`, `get_robot_status` |

Các file này là **dữ liệu gốc, tool không sửa**. Mission tạo hoặc hủy trong lúc chạy được ghi vào `missions/` (đã gitignore), để mỗi lần chạy eval bắt đầu từ cùng một trạng thái.

Mỗi robot được đặt sẵn để kích hoạt đúng một nhánh kiểm tra:

| Robot | Trạng thái | Dùng để thử |
|---|---|---|
| `AMR-01` | idle 82%, ER | Dispatch thành công |
| `AMR-02` | idle 64%, PHARMACY | Luồng chính |
| `AMR-03` | error `E_STOP_ACTIVE`, WARD_3A | `robot_unavailable` |
| `AMR-04` | on_mission `MS-0012`, 45% | `robot_unavailable`, hủy mission |
| `AMR-05` | charging 15%, DOCK_1 | `low_battery` |
