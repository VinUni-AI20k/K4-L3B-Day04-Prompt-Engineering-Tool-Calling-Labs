from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools._shared import ROOT, fold_text, terms

SALES_FILE = ROOT / "data" / "sales" / "catalog.json"
BRANCHES = {"district_1", "thu_duc", "ha_noi"}
BRANDS = {"lenovo", "dell", "asus", "hp", "apple", "acer"}
NEEDS = {"study", "office", "programming", "design", "gaming"}


def load_sales_data() -> dict[str, Any]:
    return json.loads(SALES_FILE.read_text(encoding="utf-8"))


def tool_error(tool: str, error: str, **details: Any) -> dict[str, Any]:
    return {"tool": tool, "error": error, **details}


def normalized_id(value: str) -> str:
    return value.strip().upper() if isinstance(value, str) else ""


def find_product(data: dict[str, Any], product_id: str) -> dict[str, Any] | None:
    wanted = normalized_id(product_id)
    return next((item for item in data["products"] if item["product_id"] == wanted), None)


def public_product(product: dict[str, Any]) -> dict[str, Any]:
    return dict(product)
