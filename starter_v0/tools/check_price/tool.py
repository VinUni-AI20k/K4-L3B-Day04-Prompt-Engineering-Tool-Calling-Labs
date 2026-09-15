from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CATALOG_FILE = ROOT / "pc_data" / "catalog.json"


def check_price(sku: str = "", include_stock: bool = False) -> dict[str, Any]:
    try:
        if not CATALOG_FILE.exists():
            return {"tool": "check_price", "error": "catalog_not_found"}

        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        products = data.get("products", [])

        wanted_sku = (sku or "").strip().upper()
        if not wanted_sku:
            return {"tool": "check_price", "error": "missing_sku"}

        product = next((p for p in products if p.get("sku", "").upper() == wanted_sku), None)
        if product is None:
            # Fuzzy match by sku or name
            product = next((p for p in products if wanted_sku in p.get("sku", "").upper() or wanted_sku in p.get("name", "").upper()), None)

        if product is None:
            return {"tool": "check_price", "sku": sku, "error": "sku_not_found"}

        result: dict[str, Any] = {
            "tool": "check_price",
            "sku": product.get("sku"),
            "name": product.get("name"),
            "price": product.get("price"),
            "formatted_price": f"{product.get('price', 0):,} VND".replace(",", "."),
        }

        if include_stock:
            stock = product.get("stock", 0)
            result["stock"] = stock
            result["in_stock"] = stock > 0
            result["status"] = "in_stock" if stock > 0 else "out_of_stock"

        return result
    except Exception as exc:
        return err("check_price", exc)
