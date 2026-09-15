from __future__ import annotations

from typing import Any

from tools._shared import error, period_dates, transactions_in


def get_summary(period: str, start_date: str = "", end_date: str = "") -> dict[str, Any]:
    try:
        start, end = period_dates(period, start_date, end_date)
        items = transactions_in(start, end)
        income = sum(item["amount"] for item in items if item["type"] == "income")
        expense = sum(item["amount"] for item in items if item["type"] == "expense")
        return {
            "tool": "get_summary", "period": period,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "income": income, "expense": expense, "balance": income - expense,
            "transaction_count": len(items), "currency": "VND",
        }
    except Exception as exc:
        return error("get_summary", exc)
