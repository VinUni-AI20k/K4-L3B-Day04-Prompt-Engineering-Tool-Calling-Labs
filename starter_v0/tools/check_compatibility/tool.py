from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err


CATALOG_FILE = ROOT / "pc_data" / "catalog.json"


def _get_product(sku: str, products: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not sku:
        return None
    wanted = sku.strip().upper()
    return next((p for p in products if p.get("sku", "").upper() == wanted or wanted in p.get("sku", "").upper()), None)


def check_compatibility(
    cpu_sku: str = "",
    mainboard_sku: str = "",
    ram_sku: str = "",
    gpu_sku: str = "",
    psu_sku: str = "",
    case_sku: str = "",
    cooler_sku: str = "",
    use_case: str = "",
) -> dict[str, Any]:
    try:
        if not CATALOG_FILE.exists():
            return {"tool": "check_compatibility", "error": "catalog_not_found"}

        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        products = data.get("products", [])

        issues: list[str] = []
        warnings: list[str] = []
        details: dict[str, Any] = {}

        cpu = _get_product(cpu_sku, products)
        mb = _get_product(mainboard_sku, products)
        ram = _get_product(ram_sku, products)
        gpu = _get_product(gpu_sku, products)
        psu = _get_product(psu_sku, products)
        cooler = _get_product(cooler_sku, products)

        if not cpu and cpu_sku:
            warnings.append(f"Không tìm thấy thông tin CPU với mã {cpu_sku}")
        if not mb and mainboard_sku:
            warnings.append(f"Không tìm thấy thông tin Mainboard với mã {mainboard_sku}")

        # 1. Socket check (CPU vs Mainboard)
        if cpu and mb:
            cpu_socket = str(cpu.get("socket", "")).strip().upper()
            mb_socket = str(mb.get("socket", "")).strip().upper()
            details["cpu_socket"] = cpu_socket
            details["mainboard_socket"] = mb_socket
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                issues.append(
                    f"Không tương thích Socket: CPU {cpu.get('name')} dùng socket {cpu_socket}, "
                    f"trong khi Mainboard {mb.get('name')} dùng socket {mb_socket}."
                )

        # 2. RAM standard check (RAM vs Mainboard)
        if ram and mb:
            ram_type = str(ram.get("ram_type", "")).strip().upper()
            mb_ram_types = mb.get("ram_type", [])
            if isinstance(mb_ram_types, str):
                mb_ram_types = [mb_ram_types]
            mb_ram_types_upper = [str(r).strip().upper() for r in mb_ram_types]
            details["ram_type"] = ram_type
            details["mainboard_supported_ram"] = mb_ram_types_upper
            if ram_type and mb_ram_types_upper and ram_type not in mb_ram_types_upper:
                issues.append(
                    f"Không tương thích RAM: RAM {ram.get('name')} là chuẩn {ram_type}, "
                    f"nhưng Mainboard {mb.get('name')} chỉ hỗ trợ chuẩn {', '.join(mb_ram_types_upper)}."
                )

        # 3. Cooler socket check
        if cooler and cpu:
            cooler_sockets = cooler.get("socket", [])
            if isinstance(cooler_sockets, str):
                cooler_sockets = [cooler_sockets]
            cooler_sockets_upper = [str(s).strip().upper() for s in cooler_sockets]
            cpu_socket = str(cpu.get("socket", "")).strip().upper()
            if cpu_socket and cooler_sockets_upper and cpu_socket not in cooler_sockets_upper:
                issues.append(
                    f"Tản nhiệt {cooler.get('name')} không hỗ trợ gông cắm cho socket {cpu_socket} của CPU {cpu.get('name')}."
                )

        # 4. Wattage vs PSU check
        est_wattage = 80  # Base motherboard, SSD, fans
        if cpu:
            est_wattage += cpu.get("wattage", 65)
        if gpu:
            est_wattage += gpu.get("wattage", 150)
        if ram:
            est_wattage += ram.get("wattage", 15)
        if cooler:
            est_wattage += cooler.get("wattage", 10)

        details["estimated_wattage"] = est_wattage
        if psu:
            psu_capacity = psu.get("wattage_capacity", 500)
            details["psu_capacity"] = psu_capacity
            if est_wattage > psu_capacity:
                issues.append(
                    f"Công suất nguồn không đủ: Tổng tiêu thụ ước tính {est_wattage}W vượt quá công suất định mức {psu_capacity}W của nguồn {psu.get('name')}."
                )
            elif est_wattage > psu_capacity * 0.85:
                warnings.append(
                    f"Công suất nguồn sát tải: Tổng tiêu thụ {est_wattage}W chiếm hơn 85% công suất {psu_capacity}W của nguồn {psu.get('name')}."
                )
        else:
            recommended_psu = int(((est_wattage + 150) // 50 + 1) * 50)
            details["recommended_psu_wattage"] = f"{recommended_psu}W"

        is_compatible = len(issues) == 0
        return {
            "tool": "check_compatibility",
            "compatible": is_compatible,
            "issues": issues,
            "warnings": warnings,
            "details": details,
            "status": "COMPATIBLE" if is_compatible else "INCOMPATIBLE",
        }
    except Exception as exc:
        return err("check_compatibility", exc)
