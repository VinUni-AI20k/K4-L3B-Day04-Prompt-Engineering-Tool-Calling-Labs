---
name: format_quote
track: core
kind: local_formatter
requires_env: []
inputs: [template, quote_title, items, total_price]
outputs: [markdown, template, quote_title]
side_effect: false
---
# format_quote

Định dạng danh sách linh kiện hoặc cấu hình PC thành bảng báo giá chuẩn Markdown để gửi khách hàng. Hỗ trợ 2 kiểu mẫu: `brief` (báo giá tóm tắt) và `detailed` (báo giá chi tiết kèm thông số kỹ thuật và bảo hành).
