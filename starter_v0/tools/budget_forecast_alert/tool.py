from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from tools._shared import error, read_data


def budget_forecast_alert(month: str) -> dict[str, Any]:
    try:
        year, month_number = map(int, month.split("-"))
        if not 1 <= month_number <= 12 or month != f"{year:04d}-{month_number:02d}":
            raise ValueError("month phải có định dạng YYYY-MM")
        budget = read_data("budgets.json")
        if budget["month"] != month:
            raise ValueError(f"chưa có ngân sách cho tháng {month}")

        today = date.today()
        days = calendar.monthrange(year, month_number)[1]
        elapsed = days if (year, month_number) < (today.year, today.month) else today.day if (year, month_number) == (today.year, today.month) else 0
        expenses = [item for item in read_data("transactions.json") if item["date"].startswith(month) and item["type"] == "expense"]
        spent = sum(item["amount"] for item in expenses)
        projected = round(spent / elapsed * days) if elapsed else 0
        alerts = []
        for category, config in budget["category_budgets"].items():
            category_spent = sum(item["amount"] for item in expenses if item["category"] == category)
            category_projected = round(category_spent / elapsed * days) if elapsed else 0
            used_percent = round(category_spent / config["limit"] * 100, 1)
            if used_percent >= config["alert_threshold_percent"] or category_projected > config["limit"]:
                alerts.append({"category": category, "spent": category_spent, "projected": category_projected, "limit": config["limit"], "used_percent": used_percent})

        limit = budget["total_budget_limit"]
        return {
            "tool": "budget_forecast_alert", "month": month, "spent": spent,
            "projected_expense": projected, "budget_limit": limit,
            "remaining_budget": limit - spent, "projected_overage": max(0, projected - limit),
            "status": "over_budget" if projected > limit else "on_track",
            "category_alerts": alerts, "currency": "VND",
        }
    except Exception as exc:
        return error("budget_forecast_alert", exc)
