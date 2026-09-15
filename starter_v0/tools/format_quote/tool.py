from __future__ import annotations

from typing import Any


def _line(item: dict[str, Any]) -> str:
    label = str(item.get("label") or item.get("sku") or item.get("source") or "Item").strip()
    detail = str(item.get("detail") or item.get("summary") or item.get("status") or "").strip()
    price = item.get("price")
    if price is not None and detail:
        return f"- **{label}:** {detail} ({price} USD)"
    if price is not None:
        return f"- **{label}:** {price} USD"
    return f"- **{label}:** {detail}"


def _total(findings: list[dict[str, Any]]) -> float | None:
    values = [float(item["price"]) for item in findings if isinstance(item.get("price"), (int, float))]
    return round(sum(values), 2) if values else None


def format_quote(
    findings: list[dict[str, Any]] | None = None,
    template: str = "brief",
    quote_title: str = "PC quote",
) -> dict[str, Any]:
    findings = findings or []
    lines = [_line(item) for item in findings]
    total = _total(findings)
    total_line = f"- **Total:** {total} USD" if total is not None else None

    if template == "detailed":
        body = [f"# Quote: {quote_title}", "", "## Items", *lines]
        if total_line:
            body += ["", "## Summary", total_line]
        body += ["", "## Notes", "- Prices are valid at the moment of checkout.", "- Assembly and shipping quoted separately."]
        markdown = "\n".join(body)
    elif template == "invoice":
        body = [f"# Invoice preview: {quote_title}", "", *lines]
        if total_line:
            body += ["", total_line]
        body += ["", "- Payment due on order confirmation."]
        markdown = "\n".join(body)
    else:
        body = [f"**{quote_title}**", *lines]
        if total_line:
            body.append(total_line)
        markdown = "\n".join(body)

    return {
        "tool": "format_quote",
        "template": template,
        "quote_title": quote_title,
        "finding_count": len(findings),
        "total": total,
        "markdown": markdown,
    }
