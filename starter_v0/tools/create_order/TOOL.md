---
name: create_order
track: core
kind: action
requires_env: []
inputs: [customer_id, product_id, quantity, branch, confirmed]
outputs: [order]
side_effect: local_file_write
requires_confirmation: true
---
