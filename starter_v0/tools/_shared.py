from __future__ import annotations

import json
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[1] / "finance_data"


def read_data(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def write_data(name: str, data: Any) -> None:
    (DATA_DIR / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def period_dates(period: str, start_date: str = "", end_date: str = "") -> tuple[date, date]:
    if start_date or end_date:
        if not start_date or not end_date:
            raise ValueError("start_date và end_date phải được cung cấp cùng nhau")
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    else:
        today = date.today()
        if period == "today":
            start = end = today
        elif period == "this_week":
            start, end = today - timedelta(days=today.weekday()), today
        elif period == "this_month":
            start, end = today.replace(day=1), today
        else:
            raise ValueError("period phải là today, this_week, this_month hoặc dùng đủ start_date/end_date")
    if start > end:
        raise ValueError("start_date không được sau end_date")
    return start, end


def transactions_in(start: date, end: date) -> list[dict[str, Any]]:
    return [
        item for item in read_data("transactions.json")
        if start <= date.fromisoformat(item["date"]) <= end
    ]


def category_map() -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in read_data("categories.json")}


def fold(text: str) -> str:
    value = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in value if unicodedata.category(char) != "Mn")


def error(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}
