from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from tools._shared import ROOT, err


CATALOG_FILE = ROOT / "pc_seller_data" / "catalog.json"
CUSTOMER_FILE = ROOT / "pc_seller_data" / "customers.json"
ORDER_DIR = ROOT / "orders"
VALID_DELIVERY = {"standard", "express"}
SENSITIVE_DATA_PATTERN = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code|cvv|cvc|card[ _-]?number)\b"
    r"|\b\d{13,19}\b",
    re.IGNORECASE,
)


def _load_catalog() -> dict[str, dict[str, Any]]:
    data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    return {str(item["sku"]).upper(): item for item in data["items"]}


def create_order(
    items: list[str] | None = None,
    customer_id: str = "",
    delivery_option: str = "standard",
    confirmed: bool = False,
) -> dict[str, Any]:
    if not isinstance(items, list) or not items:
        return {"tool": "create_order", "error": "missing_items"}
    if not all(isinstance(item, str) and item.strip() for item in items):
        return {"tool": "create_order", "error": "invalid_items"}

    normalized_items = [item.strip().upper() for item in items]
    joined = " ".join(normalized_items)
    if SENSITIVE_DATA_PATTERN.search(joined):
        return {
            "tool": "create_order",
            "error": "restricted_sensitive_data",
            "message": "Remove payment credentials, card numbers, tokens, and MFA values before creating an order.",
        }

    delivery = (delivery_option or "standard").strip().lower()
    if delivery not in VALID_DELIVERY:
        return {"tool": "create_order", "error": "invalid_delivery_option", "delivery_option": delivery}

    try:
        catalog = _load_catalog()
        unknown = [sku for sku in normalized_items if sku not in catalog]
        if unknown:
            return {"tool": "create_order", "error": "unknown_sku", "unknown_skus": unknown}

        customers_data = json.loads(CUSTOMER_FILE.read_text(encoding="utf-8"))
        wanted_customer = (customer_id or "").strip().upper()
        customer = next(
            (entry for entry in customers_data["customers"] if entry["customer_id"].upper() == wanted_customer),
            None,
        )
        if customer is None:
            return {"tool": "create_order", "error": "customer_not_found", "customer_id": wanted_customer}

        if confirmed is not True:
            return {
                "tool": "create_order",
                "status": "needs_confirmation",
                "message": "Create the order only after explicit user confirmation.",
                "items": normalized_items,
                "customer_id": wanted_customer,
                "delivery_option": delivery,
            }

        total = round(sum(float(catalog[sku].get("price", 0) or 0) for sku in normalized_items), 2)
        now = datetime.now(timezone.utc)
        seed = f"{now.isoformat()}|{wanted_customer}|{'|'.join(normalized_items)}|{delivery}"
        order_id = "ORD-LAB-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8].upper()
        payload = {
            "order_id": order_id,
            "customer_id": wanted_customer,
            "items": normalized_items,
            "delivery_option": delivery,
            "total": total,
            "currency": "USD",
            "created_at": now.isoformat(),
            "source": "educational_local_mock",
        }
        ORDER_DIR.mkdir(parents=True, exist_ok=True)
        path = ORDER_DIR / f"{order_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"tool": "create_order", "status": "created", **payload, "path": str(path)}
    except Exception as exc:
        return err("create_order", exc)
