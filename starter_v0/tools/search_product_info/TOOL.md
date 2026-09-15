---
name: search_product_info
track: optional
kind: live_api
provider: tavily_search
requires_env: [TAVILY_API_KEY]
inputs: [query, manufacturer, product, query_type]
outputs: [results, source, query_type]
side_effect: false
---
# search_product_info

Tìm kiếm thông tin chính thức về linh kiện hoặc máy tính trên trang của nhà sản xuất (Intel, AMD, Nvidia, ASUS, MSI, Gigabyte...).
Hỗ trợ 4 loại tra cứu (query_type): `specs` (thông số kỹ thuật), `drivers` (tải driver, BIOS), `support` (tài liệu hỗ trợ), `compatibility` (danh sách phần cứng tương thích QVL).
Chỉ truy vấn các domain chính thức, lọc bỏ thông tin nghi ngờ và không gửi thông tin bí mật ra ngoài.
