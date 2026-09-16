from __future__ import annotations
from typing import Any
from tools.sales_shared import find_product, load_sales_data, normalized_id, public_product, tool_error

def compare_products(product_ids: list[str] | None = None) -> dict[str, Any]:
    if not isinstance(product_ids, list) or len(product_ids) < 2 or not all(isinstance(item, str) and item.strip() for item in product_ids): return tool_error("compare_products", "invalid_product_ids", min_items=2)
    data = load_sales_data(); ids = [normalized_id(item) for item in product_ids]
    if len(set(ids)) != len(ids): return tool_error("compare_products", "duplicate_product_ids")
    products = [find_product(data, item) for item in ids]; missing = [item for item, product in zip(ids, products) if product is None]
    if missing: return tool_error("compare_products", "product_not_found", product_ids=missing)
    return {"tool":"compare_products", "product_ids":ids, "products":[public_product(product) for product in products if product], "snapshot_at":data["snapshot_at"]}
