---
name: lookup_vehicle
track: core
kind: local_inventory
provider: synthetic_vehicle_store
requires_env: []
inputs: [vehicle_id]
outputs: [vehicle, snapshot_at]
side_effect: false
---
# lookup_vehicle

Tra cứu một xe điện giả lập theo `vehicle_id` và kiểm tra xe thuộc tài xế đang
đăng nhập. Tool chỉ trả dữ liệu kỹ thuật cần cho việc lập phương án sạc.

