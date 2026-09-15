---
name: find_charging_offers
track: core
kind: local_status
provider: deterministic_lab_optimizer
requires_env: []
inputs: [vehicle_id, current_soc, target_soc, deadline, origin, preference, top_k, allow_partial]
outputs: [offers, excluded_candidates, snapshot_at, decision_boundary]
side_effect: false
---
# find_charging_offers

Lập và verify Top-K phương án từ dữ liệu xe, tuyến đường, connector, lịch cổng,
công suất và giá giả lập. Trợ lý không được tự sửa verdict hoặc bịa route khi
tool thiếu bằng chứng. Offer trả về chưa phải một lịch giữ chỗ.

