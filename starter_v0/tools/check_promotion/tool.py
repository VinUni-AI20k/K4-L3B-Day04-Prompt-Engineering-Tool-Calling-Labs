from __future__ import annotations
from typing import Any
from tools.sales_shared import find_product, load_sales_data, normalized_id, tool_error

def check_promotion(product_id: str = "") -> dict[str, Any]:
    if not isinstance(product_id, str) or not product_id.strip(): return tool_error("check_promotion", "missing_product_id")
    data = load_sales_data(); product_id = normalized_id(product_id)
    if not find_product(data, product_id): return tool_error("check_promotion", "product_not_found", product_id=product_id)
    return {"tool":"check_promotion", "product_id":product_id, "promotions":[item for item in data["promotions"] if item["product_id"] == product_id], "snapshot_at":data["snapshot_at"]}
