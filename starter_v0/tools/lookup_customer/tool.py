from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CUSTOMERS_FILE = ROOT / "pc_data" / "customers.json"


def lookup_customer(customer_id: str = "") -> dict[str, Any]:
    try:
        if not CUSTOMERS_FILE.exists():
            return {"tool": "lookup_customer", "error": "customers_file_not_found"}

        data = json.loads(CUSTOMERS_FILE.read_text(encoding="utf-8"))
        customers = data.get("customers", [])

        wanted_id = (customer_id or "").strip().upper()
        if not wanted_id:
            return {"tool": "lookup_customer", "error": "missing_customer_id"}

        cust = next((c for c in customers if c.get("customer_id", "").upper() == wanted_id), None)
        if cust is None:
            # Fallback check phone or name
            cust = next((c for c in customers if wanted_id in c.get("phone", "") or wanted_id in c.get("name", "").upper()), None)

        if cust is None:
            return {"tool": "lookup_customer", "customer_id": customer_id, "error": "customer_not_found"}

        return {
            "tool": "lookup_customer",
            "customer_id": cust.get("customer_id"),
            "name": cust.get("name"),
            "tier": cust.get("tier"),
            "phone": cust.get("phone"),
            "orders": cust.get("orders", []),
            "shipping_address": cust.get("shipping_address"),
            "status": "found",
        }
    except Exception as exc:
        return err("lookup_customer", exc)
