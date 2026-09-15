from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from tools._shared import ROOT, err

ASSET_FILE = ROOT / "helpdesk_data" / "assets.json"
ASSET_ID_PATTERN = re.compile(r"^(LT|PR)-\d{3}$")


def check_asset_warranty(
    asset_id: str = "",
    alert_threshold_days: int = 180,
) -> dict[str, Any]:
    """Inspect the warranty status, purchase date, and lifecycle risk of a device.
    
    This is an extended lifecycle management tool outside the core 9 helpdesk tools.
    Calculates remaining warranty days against corporate snapshot date and provides
    maintenance/replacement policy recommendations.
    """
    try:
        if not asset_id or not isinstance(asset_id, str) or not asset_id.strip():
            return {
                "tool": "check_asset_warranty",
                "error": "missing_parameter",
                "message": "asset_id is required and must be a string",
            }

        asset_id_clean = asset_id.strip().upper()
        if not ASSET_ID_PATTERN.match(asset_id_clean):
            return {
                "tool": "check_asset_warranty",
                "error": "invalid_asset_format",
                "message": f"Asset ID '{asset_id}' is invalid. Must match format 'LT-xxx' or 'PR-xxx' (e.g. LT-204).",
                "provided_id": asset_id,
            }

        data = json.loads(ASSET_FILE.read_text(encoding="utf-8"))
        assets: list[dict[str, Any]] = data.get("assets", [])
        snapshot_str = data.get("snapshot_at", "2026-09-14T09:00:00+07:00")
        snapshot_date = datetime.fromisoformat(snapshot_str).date()

        target_asset = next((a for a in assets if a.get("asset_id", "").upper() == asset_id_clean), None)
        if not target_asset:
            return {
                "tool": "check_asset_warranty",
                "error": "asset_not_found",
                "message": f"Asset '{asset_id_clean}' not found in corporate asset registry.",
                "asset_id": asset_id_clean,
            }

        warranty_str = target_asset.get("warranty_until")
        purchase_str = target_asset.get("purchase_date")

        if not warranty_str:
            return {
                "tool": "check_asset_warranty",
                "asset_id": asset_id_clean,
                "status": "unknown",
                "message": "No warranty information registered for this asset.",
                "device": {
                    "model": target_asset.get("model"),
                    "assigned_to": target_asset.get("assigned_to"),
                },
            }

        warranty_date = datetime.strptime(warranty_str, "%Y-%m-%d").date()
        days_remaining = (warranty_date - snapshot_date).days

        if days_remaining < 0:
            lifecycle_status = "expired"
            recommendation = "Device is out of warranty. Hardware repairs require special IT procurement approval or asset replacement."
        elif days_remaining <= alert_threshold_days:
            lifecycle_status = "expiring_soon"
            recommendation = f"Warranty expires in {days_remaining} days. Schedule renewal or flag for scheduled hardware refresh cycle."
        else:
            lifecycle_status = "active"
            recommendation = f"Standard coverage active ({days_remaining} days remaining). Covered under OEM SLA."

        return {
            "tool": "check_asset_warranty",
            "asset_id": asset_id_clean,
            "manufacturer": target_asset.get("manufacturer"),
            "model": target_asset.get("model"),
            "type": target_asset.get("type"),
            "assigned_to": target_asset.get("assigned_to"),
            "location": target_asset.get("location"),
            "purchase_date": purchase_str,
            "warranty_until": warranty_str,
            "days_remaining": days_remaining,
            "lifecycle_status": lifecycle_status,
            "alert_threshold_days": alert_threshold_days,
            "recommendation": recommendation,
            "snapshot_reference_date": snapshot_str,
        }
    except Exception as exc:
        return err("check_asset_warranty", exc)
