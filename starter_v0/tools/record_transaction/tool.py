from __future__ import annotations

from datetime import datetime
from typing import Any

from tools._shared import category_map, error, read_data, write_data


def record_transaction(
    type: str, amount: int, category: str, note: str = "", confirmed: bool = False
) -> dict[str, Any]:
    try:
        categories = category_map()
        if type not in {"expense", "income"}:
            raise ValueError("type phải là expense hoặc income")
        if category not in categories or categories[category]["type"] != type:
            valid = [key for key, value in categories.items() if value["type"] == type]
            raise ValueError(f"category không hợp lệ cho {type}; chọn một trong: {', '.join(valid)}")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0 or not float(amount).is_integer():
            raise ValueError("amount phải là số nguyên VND lớn hơn 0")
        preview = {"type": type, "amount": int(amount), "category": category, "note": note.strip(), "currency": "VND"}
        if not confirmed:
            return {"tool": "record_transaction", "status": "confirmation_required", "preview": preview}

        now = datetime.now()
        items = read_data("transactions.json")
        prefix = f"TXN-{now:%Y%m%d}-"
        sequence = max((int(item["id"][-3:]) for item in items if item["id"].startswith(prefix)), default=0) + 1
        transaction = {
            "id": f"{prefix}{sequence:03d}", "date": now.date().isoformat(), "time": now.strftime("%H:%M"),
            **preview, "payment_method": "other",
        }
        items.append(transaction)
        write_data("transactions.json", items)
        return {"tool": "record_transaction", "status": "recorded", "transaction": transaction}
    except Exception as exc:
        return error("record_transaction", exc)
