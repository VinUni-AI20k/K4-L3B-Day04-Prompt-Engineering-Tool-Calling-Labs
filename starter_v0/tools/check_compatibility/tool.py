from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CATALOG_FILE = ROOT / "pc_seller_data" / "catalog.json"


def _load_items() -> dict[str, dict[str, Any]]:
    data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    return {str(item["sku"]).upper(): item for item in data["items"]}


def check_compatibility(
    cpu_sku: str = "",
    mainboard_sku: str = "",
    ram_sku: str = "",
    gpu_sku: str = "",
    psu_sku: str = "",
    case_sku: str = "",
    cooler_sku: str = "",
    use_case: str = "all",
) -> dict[str, Any]:
    try:
        items = _load_items()
        requested = {
            "cpu_sku": (cpu_sku or "").strip().upper(),
            "mainboard_sku": (mainboard_sku or "").strip().upper(),
            "ram_sku": (ram_sku or "").strip().upper(),
            "gpu_sku": (gpu_sku or "").strip().upper(),
            "psu_sku": (psu_sku or "").strip().upper(),
            "case_sku": (case_sku or "").strip().upper(),
            "cooler_sku": (cooler_sku or "").strip().upper(),
        }
        resolved = {key: items.get(value) for key, value in requested.items() if value}
        missing = sorted({value for key, value in requested.items() if value and items.get(value) is None})
        if missing:
            return {
                "tool": "check_compatibility",
                "requested": requested,
                "error": "sku_not_found",
                "unknown_skus": missing,
            }

        def spec(key: str, section: str) -> Any:
            item = resolved.get(key)
            if not item:
                return None
            return (item.get("specs") or {}).get(section)

        checks: list[dict[str, Any]] = []

        def add(name: str, status: str, detail: str) -> None:
            checks.append({"check": name, "status": status, "detail": detail})

        if resolved.get("cpu_sku") and resolved.get("mainboard_sku"):
            cpu_socket = spec("cpu_sku", "socket")
            board_socket = spec("mainboard_sku", "socket")
            ok = cpu_socket == board_socket
            add("cpu_mainboard_socket", "ok" if ok else "fail", f"CPU socket {cpu_socket} vs mainboard socket {board_socket}")

        if resolved.get("mainboard_sku") and resolved.get("ram_sku"):
            board_ram = spec("mainboard_sku", "ram_type")
            ram_type = spec("ram_sku", "ram_type")
            ok = board_ram == ram_type
            add("mainboard_ram_type", "ok" if ok else "fail", f"Mainboard memory {board_ram} vs memory kit {ram_type}")

        if resolved.get("gpu_sku") and resolved.get("case_sku"):
            gpu_len = spec("gpu_sku", "length_mm")
            case_max = spec("case_sku", "max_gpu_length_mm")
            ok = gpu_len is not None and case_max is not None and gpu_len <= case_max
            add("gpu_case_clearance", "ok" if ok else "fail", f"GPU length {gpu_len} mm vs case clearance {case_max} mm")

        if resolved.get("gpu_sku") and resolved.get("psu_sku"):
            recommended = spec("gpu_sku", "recommended_psu_w")
            wattage = spec("psu_sku", "wattage")
            ok = recommended is not None and wattage is not None and wattage >= recommended
            add("psu_wattage", "ok" if ok else "fail", f"PSU {wattage} W vs recommended {recommended} W")

        if resolved.get("cpu_sku") and resolved.get("cooler_sku"):
            cpu_socket = spec("cpu_sku", "socket")
            sockets = spec("cooler_sku", "sockets") or []
            ok = cpu_socket in [str(value).upper() for value in sockets] or cpu_socket in sockets
            add("cpu_cooler_socket", "ok" if ok else "fail", f"CPU socket {cpu_socket} vs cooler sockets {sockets}")

        if not checks:
            add("coverage", "skipped", "Provide at least two compatible component keys to run a compatibility check.")

        failed = [check for check in checks if check["status"] == "fail"]
        return {
            "tool": "check_compatibility",
            "requested": {key: value for key, value in requested.items() if value},
            "use_case": (use_case or "all").strip().lower(),
            "compatible": not failed and not any(check["status"] == "skipped" for check in checks),
            "checks": checks,
            "failed_checks": [check["check"] for check in failed],
        }
    except Exception as exc:
        return err("check_compatibility", exc)
