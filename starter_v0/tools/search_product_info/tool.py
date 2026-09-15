from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

import requests

from tools._shared import TIMEOUT, err


VENDOR_DOMAINS = {
    "intel": ["intel.com", "ark.intel.com"],
    "amd": ["amd.com"],
    "nvidia": ["nvidia.com"],
    "asus": ["asus.com", "rog.asus.com"],
    "msi": ["msi.com"],
    "gigabyte": ["gigabyte.com"],
    "corsair": ["corsair.com"],
    "kingston": ["kingston.com"],
}

QUERY_LABELS = {
    "specs": "technical specifications",
    "drivers": "drivers bios and downloads",
    "support": "support documentation",
    "compatibility": "hardware compatibility qvl",
}


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _safe_external_text(value: str) -> tuple[str, list[str]]:
    safe_lines: list[str] = []
    suspicious_lines: list[str] = []
    markers = ("system:", "assistant:", "developer:", "ignore previous", "ignore all", "tool_calls_json")
    for line in (value or "").splitlines():
        if any(marker in line.casefold() for marker in markers):
            suspicious_lines.append(line.strip())
        else:
            safe_lines.append(line)
    return "\n".join(safe_lines).strip(), suspicious_lines


def search_product_info(
    query: str = "",
    manufacturer: str = "",
    product: str = "",
    query_type: str = "specs",
    max_results: int = 3,
) -> dict[str, Any]:
    try:
        norm_type = (query_type or "specs").strip().lower()
        if norm_type not in QUERY_LABELS:
            norm_type = "specs"

        mfg = (manufacturer or "").strip().lower()
        prod = (product or "").strip()
        q = (query or "").strip()

        search_query = f"{mfg} {prod} {q} {QUERY_LABELS[norm_type]}".strip()
        api_key = os.getenv("TAVILY_API_KEY", "").strip()

        # Offline fallback data if no Tavily API key or API fails
        if not api_key:
            return {
                "tool": "search_product_info",
                "source": "educational_hardware_mock",
                "query": search_query,
                "query_type": norm_type,
                "results": [
                    {
                        "title": f"{mfg.title()} {prod} Official {norm_type.title()} Guide",
                        "url": f"https://www.{mfg or 'hardware'}.com/support/products/{prod}",
                        "content": f"Official verified product documentation for {prod}. Includes architecture details, power envelope, supported interfaces and validated configurations.",
                        "domain": f"{mfg or 'hardware'}.com",
                    }
                ],
            }

        domains = VENDOR_DOMAINS.get(mfg, [])
        payload: dict[str, Any] = {
            "api_key": api_key,
            "query": search_query,
            "max_results": max(1, min(int(max_results or 3), 5)),
            "search_depth": "basic",
        }
        if domains:
            payload["include_domains"] = domains

        resp = requests.post("https://api.tavily.com/search", json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        raw_results = resp.json().get("results", [])

        results = []
        for r in raw_results:
            text, _ = _safe_external_text(r.get("content", ""))
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": text[:500],
                "domain": _domain(r.get("url", "")),
            })

        return {
            "tool": "search_product_info",
            "source": "tavily_live_search",
            "query": search_query,
            "query_type": norm_type,
            "results": results,
        }
    except Exception as exc:
        return err("search_product_info", exc)
