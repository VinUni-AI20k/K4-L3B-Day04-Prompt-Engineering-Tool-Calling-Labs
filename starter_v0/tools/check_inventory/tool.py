from __future__ import annotations
from typing import Any
from tools.sales_shared import BRANCHES, find_product, load_sales_data, normalized_id, tool_error

def check_inventory(product_id: str = "", branch: str = "") -> dict[str, Any]:
    if not isinstance(product_id, str) or not product_id.strip(): return tool_error("check_inventory", "missing_product_id")
    if not isinstance(branch, str) or not branch.strip(): return tool_error("check_inventory", "missing_branch")
    data = load_sales_data(); branch_key = branch.strip().lower()
    if branch_key not in BRANCHES: return tool_error("check_inventory", "invalid_branch", branch=branch_key)
    if not find_product(data, product_id): return tool_error("check_inventory", "product_not_found", product_id=normalized_id(product_id))
    quantity = data["inventory"][branch_key][normalized_id(product_id)]
    return {"tool":"check_inventory", "product_id":normalized_id(product_id), "branch":branch_key, "quantity":quantity, "availability":"in_stock" if quantity else "out_of_stock", "snapshot_at":data["snapshot_at"]}
