---
name: check_price
track: core
kind: local_status
requires_env: []
inputs: [sku, include_stock]
outputs: [sku, name, price, stock, in_stock]
side_effect: false
---
# check_price

Tra cứu giá niêm yết chính xác của một mã linh kiện hoặc máy tính theo mã SKU. Khi `include_stock: true`, trả về thêm số lượng tồn kho và tình trạng sẵn hàng.
