"""Provider-free smoke tests for the sales mock tools and registry."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import SALES_TOOL_FUNCTIONS, load_tool_declarations

DECLARATIONS = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")

EXPECTED = {
    "search_products": ({"query", "brand", "max_price_vnd", "need"}, set()),
    "get_product_details": ({"product_id"}, {"product_id"}),
    "check_inventory": ({"product_id", "branch"}, {"product_id", "branch"}),
    "compare_products": ({"product_ids"}, {"product_ids"}),
    "check_promotion": ({"product_id"}, {"product_id"}),
    "search_policy": ({"query", "category"}, {"query"}),
    "lookup_customer": ({"customer_id"}, {"customer_id"}),
    "get_order_status": ({"order_id"}, {"order_id"}),
    "create_order": ({"customer_id", "product_id", "quantity", "branch", "confirmed"}, {"customer_id", "product_id", "quantity", "branch"}),
}


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS {label}")


def main() -> None:
    declared = {item["name"]: item["parameters"] for item in DECLARATIONS}
    check(set(declared) == set(EXPECTED) == set(SALES_TOOL_FUNCTIONS), "registry and tools.yaml names match")
    for name, (properties, required) in EXPECTED.items():
        params = declared[name]
        check(set(params["properties"]) == properties and set(params.get("required", [])) == required, f"{name} schema fields match")

    happy = {
        "search_products": {"need": "gaming", "max_price_vnd": 35000000},
        "get_product_details": {"product_id": "PROD001"},
        "check_inventory": {"product_id": "PROD001", "branch": "district_1"},
        "compare_products": {"product_ids": ["PROD001", "PROD009"]},
        "check_promotion": {"product_id": "PROD002"},
        "search_policy": {"query": "bảo hành"},
        "lookup_customer": {"customer_id": "CUS001"},
        "get_order_status": {"order_id": "ORD001"},
        "create_order": {"customer_id": "CUS001", "product_id": "PROD001", "quantity": 1, "branch": "district_1", "confirmed": True},
    }
    errors = {
        "search_products": {"brand": "unknown"}, "get_product_details": {"product_id": "PROD999"},
        "check_inventory": {"product_id": "PROD001", "branch": "unknown"}, "compare_products": {"product_ids": ["PROD001"]},
        "check_promotion": {"product_id": "PROD999"}, "search_policy": {"query": ""},
        "lookup_customer": {"customer_id": "CUS999"}, "get_order_status": {"order_id": "ORD999"},
        "create_order": {"customer_id": "CUS001", "product_id": "PROD001", "quantity": 0, "branch": "district_1"},
    }
    for name, args in happy.items():
        result = SALES_TOOL_FUNCTIONS[name](**args)
        check("error" not in result, f"{name} happy path")
    for name, args in errors.items():
        result = SALES_TOOL_FUNCTIONS[name](**args)
        check("error" in result, f"{name} error path")


if __name__ == "__main__":
    main()
