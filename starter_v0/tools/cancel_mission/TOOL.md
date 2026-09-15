---
name: cancel_mission
track: core
kind: action
provider: local_hospital_mock
requires_env: []
inputs: [mission_id, confirmed]
outputs: [status, mission_id, robot_id, destination_id, robot_status_after, path]
side_effect: local_file_write
requires_confirmation: true
---
# cancel_mission

Records a cancellation for an existing mission under `missions/`. Returns
`invalid_mission_id` unless the ID looks like `MS-0012`, `mission_not_found`
for an unknown mission, `mission_not_cancellable` for a completed or already
cancelled mission, and `needs_confirmation` unless `confirmed` is exactly
`true`. It is not used when the operator drops a request that was never
dispatched.
