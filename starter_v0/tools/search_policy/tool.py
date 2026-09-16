from __future__ import annotations
from typing import Any
from tools._shared import terms
from tools.sales_shared import load_sales_data, tool_error

def search_policy(query: str = "", category: str = "all") -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip(): return tool_error("search_policy", "missing_query")
    if not isinstance(category, str): return tool_error("search_policy", "invalid_category")
    category_key = category.strip().lower()
    if category_key not in {"all", "warranty", "returns", "shipping"}: return tool_error("search_policy", "invalid_category", category=category_key)
    data = load_sales_data(); wanted = terms(query); results=[]
    for policy in data["policies"]:
        if category_key != "all" and policy["category"] != category_key: continue
        if wanted & terms(" ".join([policy["title"], policy["content"], policy["category"]])): results.append(dict(policy))
    return {"tool":"search_policy", "query":query, "category":category_key, "results":results, "snapshot_at":data["snapshot_at"]}
