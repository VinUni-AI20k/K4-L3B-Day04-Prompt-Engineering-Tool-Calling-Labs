---
name: budget_forecast_alert
track: bonus
kind: local_knowledge
requires_env: []
inputs: [month]
outputs: [spent, projected_expense, budget_limit, remaining_budget, status, category_alerts]
side_effect: false
---
# budget_forecast_alert

Dự báo chi tiêu cuối tháng và cảnh báo nguy cơ vượt ngân sách.
