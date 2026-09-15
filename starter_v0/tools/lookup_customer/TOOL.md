---
name: lookup_customer
track: core
kind: local_inventory
requires_env: []
inputs: [customer_id]
outputs: [customer_id, name, tier, orders, shipping_address]
side_effect: false
---
# lookup_customer

Tra cứu thông tin khách hàng thân thiết theo mã khách hàng (ví dụ: CUST-2001 đến CUST-2004). Trả về họ tên, hạng hội viên (VIP, Gold, Silver, Standard), lịch sử mã đơn hàng và địa chỉ giao hàng. Không bao giờ trả về thông tin thẻ ngân hàng hoặc thông tin nhạy cảm.
