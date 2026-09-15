---
name: get_robot_status
track: core
kind: local_status
provider: local_hospital_mock
requires_env: []
inputs: [robot_id, check]
outputs: [robot_id, check, robot, data, last_seen, snapshot_at]
side_effect: false
---
# get_robot_status

Reads one robot from the mock fleet snapshot in `hospital_data/robots.json`.
`check` narrows the answer to location, battery, errors or the current mission.
Returns `invalid_robot_id` unless the ID looks like `AMR-02`, and
`robot_not_found` for an unknown robot. It never lists the whole fleet.
