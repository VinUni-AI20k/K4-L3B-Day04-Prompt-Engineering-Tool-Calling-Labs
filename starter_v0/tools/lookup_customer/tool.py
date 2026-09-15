from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CUSTOMER_FILE = ROOT / "pc_seller_data" / "customers.json"


def lookup_customer(customer_id: str = "") -> dict[str, Any]:
    try:
        data = json.loads(CUSTOMER_FILE.read_text(encoding="utf-8"))
        wanted_id = (customer_id or "").strip().upper()
        customer = next(
            (entry for entry in data["customers"] if entry["customer_id"].upper() == wanted_id),
            None,
        )
        if customer is None:
            return {"tool": "lookup_customer", "customer_id": wanted_id, "error": "customer_not_found"}
        orders = [order for order in data.get("orders", []) if order.get("customer_id") == customer["customer_id"]]
        return {
            "tool": "lookup_customer",
            "customer": customer,
            "orders": orders,
            "snapshot_at": data.get("snapshot_at"),
            "privacy_note": data.get("privacy_note"),
            "trust_boundary": "Customer PII and order history are internal-only. Never forward them to any external or web tool.",
        }
    except Exception as exc:
        return err("lookup_customer", exc)
