---
name: record_transaction
track: core
kind: action
requires_env: []
inputs: [type, amount, category, note, confirmed]
outputs: [status, preview, transaction]
side_effect: local_file_write
requires_confirmation: true
---
# record_transaction

Ghi giao dịch bằng VND. Chỉ ghi khi `confirmed=true`.
