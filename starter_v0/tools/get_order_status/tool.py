from __future__ import annotations
from typing import Any
from tools.sales_shared import load_sales_data, normalized_id, tool_error

def get_order_status(order_id: str = "") -> dict[str, Any]:
    if not isinstance(order_id, str) or not order_id.strip(): return tool_error("get_order_status", "missing_order_id")
    data=load_sales_data(); wanted=normalized_id(order_id); order=next((item for item in data["orders"] if item["order_id"] == wanted), None)
    return {"tool":"get_order_status", "order":dict(order), "snapshot_at":data["snapshot_at"]} if order else tool_error("get_order_status", "order_not_found", order_id=wanted)
