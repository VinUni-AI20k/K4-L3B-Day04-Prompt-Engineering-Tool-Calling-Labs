---
name: create_order
track: core
kind: action
provider: local_order_store
requires_env: []
inputs: [items, customer_id, delivery_option, confirmed]
outputs: [status, order_id, items, customer_id, delivery_option, total, path]
side_effect: local_file_write
requires_confirmation: true
---
# create_order

Creates a local mock order under `orders/` for a prebuilt PC or individual
component SKUs. It returns `needs_confirmation` and writes nothing unless
`confirmed` is explicitly true. It rejects unknown SKUs, unknown customers,
invalid delivery options, and item payloads containing payment credentials,
card numbers, tokens, or MFA values.
