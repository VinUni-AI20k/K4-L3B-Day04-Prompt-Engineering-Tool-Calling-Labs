# cancel_reservation (Bonus Tool)

Hủy lịch giữ chỗ sạc đã xác nhận, tính toán hoàn phí cọc và giải phóng cổng sạc.

## Arguments
- `reservation_id` (string, required): Mã lịch đặt chỗ cần hủy (định dạng `RES-[0-9A-Z]+`).
- `reason` (string, optional): Lý do hủy lịch (mặc định: `change_of_plans`).
- `confirmed` (boolean, required): Phải là `true` sau khi người dùng xác nhận rõ ràng ý định hủy.
