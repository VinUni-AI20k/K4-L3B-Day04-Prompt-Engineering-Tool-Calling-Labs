---
name: list_robots
track: core
kind: local_status
provider: local_hospital_mock
requires_env: []
inputs: [status, min_battery]
outputs: [filters, count, robots, snapshot_at]
side_effect: false
---
# list_robots

Filters the mock fleet by status and minimum battery percentage, sorted by
robot ID. Use it when the operator has not named a robot. Returns
`invalid_status` or `invalid_min_battery` for values outside the declared range.
