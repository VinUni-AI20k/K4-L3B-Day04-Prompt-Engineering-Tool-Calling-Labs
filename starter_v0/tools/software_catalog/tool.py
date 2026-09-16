from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text


CATALOG_FILE = ROOT / "helpdesk_data" / "software_catalog.json"


def search_software_catalog(software_name: str = "", category: str = "all") -> dict[str, Any]:
    """Tra cứu danh mục phần mềm nội bộ, trạng thái phê duyệt, bản quyền và hướng dẫn cài đặt."""
    try:
        query = (software_name or "").strip()
        if not query:
            return {
                "tool": "software_catalog",
                "error": "missing_software_name",
                "message": "Vui lòng cung cấp tên phần mềm cần tra cứu.",
            }

        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        catalog: list[dict[str, Any]] = data.get("catalog", [])

        query_folded = fold_text(query)
        cat_filter = (category or "all").strip().lower()

        matched_item = None
        for item in catalog:
            if cat_filter != "all" and item.get("category", "").lower() != cat_filter:
                continue

            name_folded = fold_text(item.get("name", ""))
            aliases_folded = [fold_text(a) for a in item.get("aliases", [])]

            if query_folded == name_folded or query_folded in aliases_folded:
                matched_item = item
                break
            # Partial match if query is distinct enough
            if len(query_folded) >= 3 and (query_folded in name_folded or any(query_folded in a for a in aliases_folded)):
                matched_item = item
                break

        if matched_item is None:
            return {
                "tool": "software_catalog",
                "software_name": query,
                "found": false if False else False,
                "error": "software_not_found",
                "message": f"Phần mềm '{query}' không có trong danh mục nội bộ của Northstar Labs. Vui lòng liên hệ IT Helpdesk hoặc tạo yêu cầu đánh giá an ninh phần mềm.",
            }

        return {
            "tool": "software_catalog",
            "software_name": matched_item["name"],
            "found": True,
            "category": matched_item["category"],
            "approval_status": matched_item["approval_status"],
            "version": matched_item["version"],
            "license_required": matched_item["license_required"],
            "license_type": matched_item["license_type"],
            "install_method": matched_item["install_method"],
            "notes": matched_item["notes"],
        }
    except Exception as exc:
        return err("software_catalog", exc)
