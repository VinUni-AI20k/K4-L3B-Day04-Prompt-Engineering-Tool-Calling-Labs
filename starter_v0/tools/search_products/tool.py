from __future__ import annotations
from typing import Any
from tools.sales_shared import BRANDS, NEEDS, load_sales_data, public_product, tool_error

def search_products(query: str = "", brand: str = "all", max_price_vnd: int | None = None, need: str = "all") -> dict[str, Any]:
    tool = "search_products"
    if not isinstance(query, str) or not isinstance(brand, str) or not isinstance(need, str): return tool_error(tool, "invalid_argument_type")
    if max_price_vnd is not None and (not isinstance(max_price_vnd, int) or isinstance(max_price_vnd, bool) or max_price_vnd <= 0): return tool_error(tool, "invalid_max_price_vnd")
    brand_key, need_key = brand.strip().lower(), need.strip().lower()
    if brand_key != "all" and brand_key not in BRANDS: return tool_error(tool, "invalid_brand", brand=brand_key)
    if need_key != "all" and need_key not in NEEDS: return tool_error(tool, "invalid_need", need=need_key)
    query_terms = set(query.lower().split())
    results = []
    for product in load_sales_data()["products"]:
        text = " ".join([product["brand"], product["name"], product["cpu"], *product["needs"]]).lower()
        if (brand_key == "all" or product["brand"].lower() == brand_key) and (need_key == "all" or need_key in product["needs"]) and (max_price_vnd is None or product["price_vnd"] <= max_price_vnd) and (not query_terms or query_terms.issubset(set(text.split()))): results.append(public_product(product))
    return {"tool": tool, "query": query, "brand": brand_key, "max_price_vnd": max_price_vnd, "need": need_key, "results": results, "snapshot_at": load_sales_data()["snapshot_at"]}
