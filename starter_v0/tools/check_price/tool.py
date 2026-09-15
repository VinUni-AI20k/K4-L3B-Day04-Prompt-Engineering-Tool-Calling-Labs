from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CATALOG_FILE = ROOT / "pc_seller_data" / "catalog.json"


def check_price(sku: str = "", include_stock: bool = True) -> dict[str, Any]:
    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        wanted_sku = (sku or "").strip().upper()
        item = next((entry for entry in data["items"] if entry["sku"].upper() == wanted_sku), None)
        if item is None:
            return {
                "tool": "check_price",
                "sku": wanted_sku,
                "error": "sku_not_found",
                "available_categories": sorted({str(entry.get("category")) for entry in data["items"]}),
            }
        result: dict[str, Any] = {
            "tool": "check_price",
            "sku": item["sku"],
            "name": item["name"],
            "category": item["category"],
            "price": item["price"],
            "currency": data.get("currency", "USD"),
            "snapshot_at": data.get("snapshot_at"),
        }
        if include_stock:
            stock = int(item.get("stock", 0) or 0)
            result["stock"] = stock
            result["in_stock"] = stock > 0
        if item.get("category") == "prebuilt":
            result["installed_skus"] = item.get("specs", {})
        return result
    except Exception as exc:
        return err("check_price", exc)
