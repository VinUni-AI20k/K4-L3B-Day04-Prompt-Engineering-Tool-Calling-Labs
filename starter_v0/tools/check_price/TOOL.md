---
name: check_price
track: core
kind: local_status
provider: pc_seller_data/catalog.json
requires_env: []
inputs: [sku, include_stock]
outputs: [sku, name, price, currency, stock, in_stock, snapshot_at]
side_effect: false
---
# check_price

Returns the current listed price for one SKU and, when `include_stock` is true,
the stock level and an `in_stock` flag. Unknown SKUs return
`error: sku_not_found`.
