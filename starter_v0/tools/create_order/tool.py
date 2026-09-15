from __future__ import annotations
import hashlib, json
from typing import Any
from tools._shared import ROOT
from tools.sales_shared import BRANCHES, find_product, load_sales_data, normalized_id, tool_error

ORDER_DIR = ROOT / "sales_orders"
def create_order(customer_id: str = "", product_id: str = "", quantity: int = 0, branch: str = "", confirmed: bool = False) -> dict[str, Any]:
    tool="create_order"
    if not all(isinstance(value, str) and value.strip() for value in [customer_id, product_id, branch]): return tool_error(tool, "missing_required_field")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0: return tool_error(tool, "invalid_quantity")
    if not isinstance(confirmed, bool): return tool_error(tool, "invalid_confirmed")
    data=load_sales_data(); customer_id, product_id, branch=normalized_id(customer_id), normalized_id(product_id), branch.strip().lower()
    if not any(item["customer_id"] == customer_id for item in data["customers"]): return tool_error(tool, "customer_not_found", customer_id=customer_id)
    if not find_product(data, product_id): return tool_error(tool, "product_not_found", product_id=product_id)
    if branch not in BRANCHES: return tool_error(tool, "invalid_branch", branch=branch)
    if data["inventory"][branch][product_id] < quantity: return tool_error(tool, "insufficient_inventory", available=data["inventory"][branch][product_id])
    if confirmed is not True: return {"tool":tool, "status":"needs_confirmation", "payload":{"customer_id":customer_id,"product_id":product_id,"quantity":quantity,"branch":branch}}
    order_id="NEW" + hashlib.sha256(f"{customer_id}|{product_id}|{quantity}|{branch}".encode()).hexdigest()[:8].upper()
    payload={"order_id":order_id,"customer_id":customer_id,"product_id":product_id,"quantity":quantity,"branch":branch,"status":"confirmed","source":"local_mock"}
    ORDER_DIR.mkdir(parents=True, exist_ok=True); (ORDER_DIR / f"{order_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"tool":tool,"status":"created","order":payload}
