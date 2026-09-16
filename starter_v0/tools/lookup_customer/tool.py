from __future__ import annotations
from typing import Any
from tools.sales_shared import load_sales_data, normalized_id, tool_error

def lookup_customer(customer_id: str = "") -> dict[str, Any]:
    if not isinstance(customer_id, str) or not customer_id.strip(): return tool_error("lookup_customer", "missing_customer_id")
    data=load_sales_data(); wanted=normalized_id(customer_id); customer=next((item for item in data["customers"] if item["customer_id"] == wanted), None)
    return {"tool":"lookup_customer", "customer":dict(customer), "snapshot_at":data["snapshot_at"]} if customer else tool_error("lookup_customer", "customer_not_found", customer_id=wanted)
