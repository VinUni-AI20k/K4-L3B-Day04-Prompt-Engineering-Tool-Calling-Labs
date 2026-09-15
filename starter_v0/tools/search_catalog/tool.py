from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, terms


CATALOG_FILE = ROOT / "pc_data" / "catalog.json"


def search_catalog(
    category: str = "",
    use_case: str = "",
    budget_max: float | int | None = None,
    query: str = "",
) -> dict[str, Any]:
    try:
        if not CATALOG_FILE.exists():
            return {"tool": "search_catalog", "error": "catalog_not_found", "items": []}

        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        products = data.get("products", [])

        wanted_category = (category or "").strip().lower()
        wanted_use_case = (use_case or "").strip().lower()
        query_terms = terms(query) if query else set()

        matches: list[dict[str, Any]] = []
        for p in products:
            # Filter by category if specified
            if wanted_category and p.get("category", "").lower() != wanted_category:
                continue

            # Filter by use_case if specified
            if wanted_use_case:
                prod_use_cases = [u.lower() for u in p.get("use_case", [])]
                if wanted_use_case not in prod_use_cases:
                    continue

            # Filter by budget_max if specified
            if budget_max is not None:
                try:
                    max_val = float(budget_max)
                    if p.get("price", 0) > max_val:
                        continue
                except (ValueError, TypeError):
                    pass

            # Filter by query terms if specified
            if query_terms:
                searchable_text = " ".join([
                    p.get("sku", ""),
                    p.get("name", ""),
                    p.get("category", ""),
                    " ".join(p.get("use_case", [])),
                    p.get("description", ""),
                    p.get("socket", ""),
                ])
                prod_terms = terms(searchable_text)
                if not (query_terms & prod_terms):
                    continue

            matches.append(p)

        return {
            "tool": "search_catalog",
            "total_found": len(matches),
            "items": matches[:10],
        }
    except Exception as exc:
        return err("search_catalog", exc)
