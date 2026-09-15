---
name: create_order
track: core
kind: action
requires_env: []
inputs: [customer_id, items, delivery_option, confirmed, shipping_address]
outputs: [order_id, status, total_price, path]
side_effect: local_file_write
requires_confirmation: true
---
# create_order

Tạo đơn đặt hàng mua máy tính hoặc linh kiện PC vào hệ thống.
CHÚ Ý AN TOÀN: Đây là công cụ có side-effect ghi dữ liệu. Tool này BẮT BUỘC có sự xác nhận rõ ràng (`confirmed: true`) từ khách hàng trước khi gọi. Nếu `confirmed: false`, tool sẽ từ chối và trả về yêu cầu xác nhận.
Các phương thức giao hàng hỗ trợ (delivery_option): `standard` (tiêu chuẩn), `express` (hỏa tốc).
