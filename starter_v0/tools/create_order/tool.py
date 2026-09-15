from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from tools._shared import ROOT, err


ORDERS_DIR = ROOT / "orders"
ORDERS_DATA_FILE = ROOT / "pc_data" / "orders.json"
CATALOG_FILE = ROOT / "pc_data" / "catalog.json"


def create_order(
    customer_id: str = "",
    items: list[dict[str, Any]] | list[str] | None = None,
    delivery_option: str = "standard",
    confirmed: bool = False,
    shipping_address: str = "",
) -> dict[str, Any]:
    try:
        norm_delivery = (delivery_option or "standard").strip().lower()
        if norm_delivery not in {"standard", "express"}:
            return {
                "tool": "create_order",
                "error": "invalid_delivery_option",
                "message": f"delivery_option '{delivery_option}' không hợp lệ. Chọn 'standard' hoặc 'express'.",
            }

        # Boundary check: Requires explicit confirmation
        if confirmed is not True:
            return {
                "tool": "create_order",
                "status": "needs_confirmation",
                "message": "Chỉ tạo đơn hàng sau khi có sự đồng ý hoặc xác nhận rõ ràng từ khách hàng.",
            }

        # Normalize items and calculate total
        clean_items: list[dict[str, Any]] = []
        total_price = 0

        # Load catalog for price reference if needed
        catalog_map: dict[str, dict[str, Any]] = {}
        if CATALOG_FILE.exists():
            try:
                cat_data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
                for prod in cat_data.get("products", []):
                    catalog_map[prod.get("sku", "").upper()] = prod
            except Exception:
                pass

        raw_items = items or []
        for it in raw_items:
            if isinstance(it, dict):
                sku = str(it.get("sku") or "").upper()
                name = it.get("name") or (catalog_map.get(sku, {}).get("name") if sku else "Linh kiện PC")
                price = it.get("price") or (catalog_map.get(sku, {}).get("price", 0) if sku else 0)
                qty = it.get("quantity") or it.get("qty") or 1
                try:
                    price_val = float(price)
                    qty_val = int(qty)
                except (ValueError, TypeError):
                    price_val = 0
                    qty_val = 1
                clean_items.append({"sku": sku, "name": name, "quantity": qty_val, "price": price_val})
                total_price += price_val * qty_val
            elif isinstance(it, str):
                sku = it.strip().upper()
                prod = catalog_map.get(sku)
                if prod:
                    price_val = float(prod.get("price", 0))
                    clean_items.append({"sku": sku, "name": prod.get("name"), "quantity": 1, "price": price_val})
                    total_price += price_val
                else:
                    clean_items.append({"sku": sku, "name": sku, "quantity": 1, "price": 0})

        now = datetime.now(timezone.utc)
        seed = f"{now.isoformat()}|{customer_id}|{total_price}|{norm_delivery}"
        order_id = "ORD-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:6].upper()

        order_record = {
            "order_id": order_id,
            "customer_id": (customer_id or "GUEST").strip().upper(),
            "items": clean_items,
            "total_price": total_price,
            "delivery_option": norm_delivery,
            "shipping_address": shipping_address or None,
            "status": "created",
            "created_at": now.isoformat(),
        }

        # Write to orders/
        ORDERS_DIR.mkdir(parents=True, exist_ok=True)
        order_file = ORDERS_DIR / f"{order_id}.json"
        order_file.write_text(json.dumps(order_record, ensure_ascii=False, indent=2), encoding="utf-8")

        # Also append to pc_data/orders.json if it exists
        if ORDERS_DATA_FILE.exists():
            try:
                orders_data = json.loads(ORDERS_DATA_FILE.read_text(encoding="utf-8"))
                orders_data.setdefault("orders", []).append(order_record)
                ORDERS_DATA_FILE.write_text(json.dumps(orders_data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass

        return {
            "tool": "create_order",
            "status": "created",
            "order_id": order_id,
            "total_price": total_price,
            "formatted_price": f"{int(total_price):,} VND".replace(",", ".") if total_price else "0 VND",
            "delivery_option": norm_delivery,
            "path": str(order_file),
        }
    except Exception as exc:
        return err("create_order", exc)
