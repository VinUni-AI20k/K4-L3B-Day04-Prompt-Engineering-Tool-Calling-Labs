from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from tools._shared import ROOT, err

ASSET_FILE = ROOT / "helpdesk_data" / "assets.json"
WARRANTY_EXPIRING_DAYS = 30


def check_asset_warranty(asset_id: str = "") -> dict[str, Any]:
    """
    Check warranty status for a company asset.

    Returns:
        asset_id: The queried asset ID
        model: Device model name
        purchase_date: Purchase date
        warranty_until: Warranty expiration date
        warranty_status: "active", "expired", or "expiring_soon"
        days_remaining: Days until warranty expires (negative if expired)
    """
    try:
        data = json.loads(ASSET_FILE.read_text(encoding="utf-8"))
        wanted_id = (asset_id or "").strip().upper()
        asset = next(
            (item for item in data["assets"] if item["asset_id"] == wanted_id),
            None,
        )
        if asset is None:
            return {"tool": "check_asset_warranty", "asset_id": wanted_id, "error": "asset_not_found"}

        warranty_until_str = asset.get("warranty_until", "")
        if not warranty_until_str:
            return {
                "tool": "check_asset_warranty",
                "asset_id": wanted_id,
                "error": "warranty_unknown",
                "message": "Warranty information is not available for this asset.",
            }

        now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        warranty_until = datetime.fromisoformat(warranty_until_str).replace(tzinfo=timezone.utc)
        days_remaining = (warranty_until - now).days

        if days_remaining < 0:
            warranty_status = "expired"
        elif days_remaining <= WARRANTY_EXPIRING_DAYS:
            warranty_status = "expiring_soon"
        else:
            warranty_status = "active"

        return {
            "tool": "check_asset_warranty",
            "asset_id": wanted_id,
            "model": asset.get("model", "Unknown"),
            "purchase_date": asset.get("purchase_date", ""),
            "warranty_until": warranty_until_str,
            "warranty_status": warranty_status,
            "days_remaining": days_remaining,
        }
    except Exception as exc:
        return err("check_asset_warranty", exc)
