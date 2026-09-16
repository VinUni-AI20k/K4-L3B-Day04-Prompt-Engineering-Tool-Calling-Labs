"""Smoke test for bonus tool: software_catalog.

Tests:
1. Tool registry and tools.yaml declaration presence.
2. Approved free software lookup (e.g. VS Code).
3. Approved license-required software lookup (e.g. Docker Desktop).
4. Restricted software lookup (e.g. Wireshark).
5. Prohibited software lookup (e.g. BitTorrent).
6. Nonexistent software lookup (software_not_found error handling).
7. Missing software name input handling.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import TOOL_FUNCTIONS, load_tool_declarations


def test_software_catalog() -> None:
    print("=" * 60)
    print("SMOKE TEST: software_catalog (Bonus Technical Tool)")
    print("=" * 60)

    # 1. Registry & YAML check
    assert "software_catalog" in TOOL_FUNCTIONS, "software_catalog must be in TOOL_FUNCTIONS"
    declarations = load_tool_declarations(ROOT / "artifacts" / "tools.yaml")
    decl = next((d for d in declarations if d["name"] == "software_catalog"), None)
    assert decl is not None, "software_catalog must be declared in tools.yaml"
    print("[PASS] Registry and tools.yaml schema check passed.")

    tool_fn = TOOL_FUNCTIONS["software_catalog"]

    # 2. Approved free software (VS Code)
    res_vscode = tool_fn(software_name="vscode")
    assert res_vscode.get("found") is True, "Expected found=True for vscode"
    assert res_vscode.get("approval_status") == "approved", "Expected approved status"
    assert res_vscode.get("license_required") is False, "Expected no license required"
    print(f"[PASS] VS Code test: {res_vscode['software_name']} -> status={res_vscode['approval_status']}, license_required={res_vscode['license_required']}")

    # 3. Approved license-required software (Docker Desktop)
    res_docker = tool_fn(software_name="Docker Desktop")
    assert res_docker.get("found") is True
    assert res_docker.get("approval_status") == "approved"
    assert res_docker.get("license_required") is True
    print(f"[PASS] Docker Desktop test: license_required={res_docker['license_required']}, method={res_docker['install_method']}")

    # 4. Restricted software (Wireshark)
    res_wireshark = tool_fn(software_name="Wireshark")
    assert res_wireshark.get("found") is True
    assert res_wireshark.get("approval_status") == "restricted"
    print(f"[PASS] Wireshark test: approval_status={res_wireshark['approval_status']}, notes={res_wireshark['notes']}")

    # 5. Prohibited software (BitTorrent)
    res_torrent = tool_fn(software_name="utorrent")
    assert res_torrent.get("found") is True
    assert res_torrent.get("approval_status") == "prohibited"
    print(f"[PASS] BitTorrent/uTorrent test: approval_status={res_torrent['approval_status']}")

    # 6. Unknown software (graceful error handling)
    res_unknown = tool_fn(software_name="UnknownMalwareApp123")
    assert res_unknown.get("found") is False
    assert res_unknown.get("error") == "software_not_found"
    print(f"[PASS] Non-existent software test: error={res_unknown['error']}")

    # 7. Missing input handling
    res_missing = tool_fn(software_name="")
    assert res_missing.get("error") == "missing_software_name"
    print(f"[PASS] Missing input test: error={res_missing['error']}")

    print("=" * 60)
    print("ALL 7 SMOKE TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 60)


if __name__ == "__main__":
    test_software_catalog()
