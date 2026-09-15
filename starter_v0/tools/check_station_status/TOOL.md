---
name: check_station_status
track: core
kind: local_status
provider: synthetic_station_snapshot
requires_env: []
inputs: [station_id]
outputs: [station, snapshot_at]
side_effect: false
---
# check_station_status

Đọc snapshot giả lập của đúng một trạm: trạng thái, connector, cổng khả dụng,
công suất và giá. Tool không tự lập phương án sạc.

