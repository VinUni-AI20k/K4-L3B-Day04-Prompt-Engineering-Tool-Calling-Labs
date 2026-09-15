from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import TOOL_FUNCTIONS


def test_check_asset_warranty():
    func = TOOL_FUNCTIONS.get("check_asset_warranty")
    assert func is not None, "check_asset_warranty not registered in TOOL_FUNCTIONS"

    # Case 1: Valid asset (active warranty)
    res1 = func(asset_id="LT-204")
    print("[1] Valid asset LT-204:", res1)
    assert res1.get("asset_id") == "LT-204"
    assert res1.get("lifecycle_status") in ["active", "expiring_soon", "expired"]
    assert "days_remaining" in res1
    assert "recommendation" in res1

    # Case 2: Invalid asset format
    res2 = func(asset_id="laptop-abc")
    print("[2] Invalid format test:", res2)
    assert res2.get("error") == "invalid_asset_format"

    # Case 3: Asset not found
    res3 = func(asset_id="LT-999")
    print("[3] Not found test:", res3)
    assert res3.get("error") == "asset_not_found"

    # Case 4: Missing parameter
    res4 = func(asset_id="")
    print("[4] Missing parameter test:", res4)
    assert res4.get("error") == "missing_parameter"

    print("\n✅ All bonus tool unit tests PASSED successfully!")


if __name__ == "__main__":
    test_check_asset_warranty()
