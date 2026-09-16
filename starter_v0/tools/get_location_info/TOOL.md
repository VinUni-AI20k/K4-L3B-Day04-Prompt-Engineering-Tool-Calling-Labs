---
name: get_location_info
track: core
kind: local_knowledge
provider: local_hospital_mock
requires_env: []
inputs: [location_id]
outputs: [location_id, location, snapshot_at]
side_effect: false
---
# get_location_info

Reads one hospital location from `hospital_data/locations.json`: floor, zone,
whether it is restricted and whether AMRs may enter. Accepts only the fixed
location IDs (for example `LAB_B`, not "Lab B") and returns
`location_not_found` with the valid list otherwise.
