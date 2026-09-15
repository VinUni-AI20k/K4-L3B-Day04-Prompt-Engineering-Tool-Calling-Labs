from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools._shared import ROOT, err, fold_text, terms


POLICY_DIR = ROOT / "tourism_data" / "policy"


def _load_doc(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            return dict(yaml.safe_load(parts[1]) or {}), parts[2].strip()
    return {}, raw.strip()


def search_travel_policy(query: str = "", policy_area: str = "all", top_k: int = 3) -> dict[str, Any]:
    """Search VietTravel internal policy documents."""
    try:
        query_terms = terms(query)
        wanted_area = (policy_area or "all").strip().lower()
        hits: list[dict[str, Any]] = []
        for path in sorted(POLICY_DIR.glob("*.md")):
            meta, body = _load_doc(path)
            doc_area = str(meta.get("policy_area") or "general").lower()
            if wanted_area != "all" and wanted_area != doc_area:
                continue
            haystack = " ".join([
                str(meta.get("title") or path.stem),
                doc_area,
                " ".join(str(tag) for tag in meta.get("tags", [])),
                body,
            ])
            score = len(query_terms & terms(haystack))
            if score <= 0:
                continue
            hits.append({
                "policy_id": meta.get("policy_id") or path.stem,
                "title": meta.get("title") or path.stem,
                "policy_area": doc_area,
                "excerpt": body[:2400],
                "source": "VietTravel Policy Library",
                "updated_at": str(meta.get("updated_at") or "unknown"),
                "score": score,
            })
        hits.sort(key=lambda item: (-item["score"], item["policy_id"]))
        return {
            "tool": "travel_policy",
            "query": query,
            "policy_area": wanted_area,
            "results": hits[: max(1, int(top_k or 3))],
            "freshness": "static_lab_data",
        }
    except Exception as exc:
        return err("travel_policy", exc)
