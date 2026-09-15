from __future__ import annotations

from typing import Any

from tools._shared import category_map, error, period_dates, transactions_in


def get_category_breakdown(period: str, category: str) -> dict[str, Any]:
    try:
        categories = category_map()
        if category not in categories:
            raise ValueError(f"category không hợp lệ; chọn một trong: {', '.join(categories)}")
        start, end = period_dates(period)
        items = [item for item in transactions_in(start, end) if item["category"] == category]
        return {
            "tool": "get_category_breakdown", "period": period,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "category": category, "category_name": categories[category]["name"],
            "total_amount": sum(item["amount"] for item in items),
            "transaction_count": len(items), "currency": "VND", "transactions": items,
        }
    except Exception as exc:
        return error("get_category_breakdown", exc)
