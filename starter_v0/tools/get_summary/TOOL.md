---
name: get_summary
track: core
kind: local_knowledge
requires_env: []
inputs: [period, start_date, end_date]
outputs: [income, expense, balance, transaction_count, currency]
side_effect: false
---
# get_summary

Tổng hợp thu, chi và số dư theo ngày, tuần, tháng hoặc khoảng ngày tùy chọn.
