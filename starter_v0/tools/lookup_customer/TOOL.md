---
name: lookup_customer
track: core
kind: local_inventory
provider: pc_seller_data/customers.json
requires_env: []
inputs: [customer_id]
outputs: [customer, orders, snapshot_at, privacy_note, trust_boundary]
side_effect: false
---
# lookup_customer

Returns one customer profile and their orders from the fictional store
database. The response contains synthetic PII and order history that are
internal-only and must never be forwarded to an external or web tool. Unknown
IDs return `error: customer_not_found`.
