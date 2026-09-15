---
name: create_reservation
track: core
kind: action
provider: local_reservation_store
requires_env: []
inputs: [offer_id, confirmed]
outputs: [status, reservation_id, offer_id, reverified]
side_effect: local_file_write
requires_confirmation: true
---
# create_reservation

Tạo lịch sạc giả lập từ một offer đã verify. Chỉ gọi với `confirmed=true` sau
khi người dùng xác nhận rõ đúng offer hiện tại. Tool kiểm tra lại quyền sở hữu,
verdict và trạng thái trạm trước khi ghi vào `reservations/`.

