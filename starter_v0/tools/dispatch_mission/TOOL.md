---
name: dispatch_mission
track: core
kind: action
provider: local_hospital_mock
requires_env: []
inputs: [robot_id, destination_id, mission_type, priority, confirmed]
outputs: [status, mission_id, robot_id, destination_id, mission_type, priority, eta_min, path]
side_effect: local_file_write
requires_confirmation: true
---
# dispatch_mission

Creates a mock mission record under `missions/`. Guards run in order and the
first failure returns an error without writing anything:

1. `invalid_robot_id`, `invalid_destination_id`, `invalid_mission_type`, `invalid_priority`
2. `robot_not_found`
3. `invalid_destination_for_mission_type` — `return_to_base` must target `DOCK_1`
4. `restricted_destination` — ICU, OR_1
5. `robot_unavailable` — robot in `error` or `on_mission`
6. `low_battery` — below `dispatch_min_battery_pct`, except `return_to_base`
7. `needs_confirmation` — unless `confirmed` is exactly `true`

Robot state is read from the seed snapshot, so a created mission does not change
later tool results. The tool has no motion controls and no free-text field.
