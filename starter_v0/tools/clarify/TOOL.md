---
name: clarify
track: core
kind: control
requires_env: []
inputs: [question, response_type, missing_fields]
outputs: [question, response_type, missing_fields, awaiting_user]
side_effect: false
---
# clarify

Hỏi lại khi thiếu dữ liệu hoặc cần xác nhận. Không ghi dữ liệu.
