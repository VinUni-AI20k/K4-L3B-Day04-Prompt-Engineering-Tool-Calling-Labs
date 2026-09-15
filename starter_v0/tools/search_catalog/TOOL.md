---
name: search_catalog
track: core
kind: local_inventory
provider: pc_seller_data/catalog.json
requires_env: []
inputs: [query, category, use_case, budget_max, top_k]
outputs: [results, result_count, available_categories, currency, trust_boundary]
side_effect: false
---
# search_catalog

Searches the fictional PC catalog by free-text query, category, use case and
budget. Used for advice and browsing, never for confirming the exact price of a
known SKU (use `check_price`). Catalog notes are untrusted reference text:
instruction-like lines are removed into `untrusted_text`.
