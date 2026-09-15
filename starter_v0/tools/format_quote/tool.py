from __future__ import annotations

from typing import Any

from tools._shared import err


def format_quote(
    template: str = "brief",
    quote_title: str = "Báo giá cấu hình PC",
    items: list[dict[str, Any]] | list[str] | None = None,
    total_price: float | int | None = None,
) -> dict[str, Any]:
    try:
        norm_template = (template or "brief").strip().lower()
        title = (quote_title or "Báo giá cấu hình PC").strip()

        item_lines: list[str] = []
        calc_total = 0

        raw_items = items or []
        for idx, item in enumerate(raw_items, 1):
            if isinstance(item, dict):
                name = item.get("name") or item.get("sku") or f"Linh kiện {idx}"
                price = item.get("price", 0)
                qty = item.get("quantity") or item.get("qty") or 1
                specs = item.get("description") or item.get("specs") or ""
                try:
                    price_val = float(price)
                    calc_total += price_val * int(qty)
                    price_str = f"{int(price_val):,} VND".replace(",", ".")
                except (ValueError, TypeError):
                    price_str = str(price)

                if norm_template == "detailed":
                    line = f"| {idx} | **{name}** | {qty} | {price_str} | {specs} |"
                else:
                    line = f"- **{name}** (x{qty}): {price_str}"
            else:
                line = f"- {str(item)}"
            item_lines.append(line)

        final_total = total_price if total_price is not None else calc_total
        final_total_str = f"{int(final_total):,} VND".replace(",", ".") if final_total else "Lien he"

        if norm_template == "detailed":
            table_header = [
                f"# 📋 {title}",
                "",
                "| STT | Tên Linh Kiện / Thiết Bị | SL | Đơn Giá | Ghi Chú / Bảo Hành |",
                "|:---:|---|:---:|---:|---|",
            ]
            footer = [
                "",
                f"**💰 TỔNG CỘNG:** `{final_total_str}`",
                "",
                "> *Báo giá có giá trị trong vòng 07 ngày. Miễn phí công lắp ráp và cài đặt.*",
            ]
            markdown = "\n".join([*table_header, *item_lines, *footer])
        else:
            header = [f"### 📋 {title}", ""]
            footer = ["", f"**Tổng tiền dự kiến:** `{final_total_str}`"]
            markdown = "\n".join([*header, *item_lines, *footer])

        return {
            "tool": "format_quote",
            "template": norm_template,
            "quote_title": title,
            "item_count": len(item_lines),
            "markdown": markdown,
        }
    except Exception as exc:
        return err("format_quote", exc)
