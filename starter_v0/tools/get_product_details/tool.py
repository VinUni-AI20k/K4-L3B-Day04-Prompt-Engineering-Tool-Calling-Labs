from __future__ import annotations
from typing import Any
from tools.sales_shared import find_product, load_sales_data, normalized_id, public_product, tool_error

def get_product_details(product_id: str = "") -> dict[str, Any]:
    if not isinstance(product_id, str) or not product_id.strip(): return tool_error("get_product_details", "missing_product_id")
    data = load_sales_data(); product = find_product(data, product_id)
    return {"tool":"get_product_details", "product":public_product(product), "snapshot_at":data["snapshot_at"]} if product else tool_error("get_product_details", "product_not_found", product_id=normalized_id(product_id))
