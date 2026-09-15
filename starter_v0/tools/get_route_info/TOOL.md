---
name: get_route_info
track: core
kind: local_status
provider: local_hospital_mock
requires_env: []
inputs: [robot_id, destination_id]
outputs: [robot_id, from_location_id, destination_id, distance_m, eta_min, elevator, elevator_status, blocked_segments, snapshot_at]
side_effect: false
---
# get_route_info

Looks up the route from a robot's current location to a destination in
`hospital_data/routes.json`: distance, ETA, elevator and blocked corridor
segments. It is read-only and never creates a mission. Returns zero distance
when the robot is already at the destination.
