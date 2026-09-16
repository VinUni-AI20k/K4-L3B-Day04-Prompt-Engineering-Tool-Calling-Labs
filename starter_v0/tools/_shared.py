from __future__ import annotations

import re
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}


# Execution-owned authorization: never populated from model arguments or text.

_TICKET_AUTHORIZATION: ContextVar[tuple[str, str, str] | None] = ContextVar(
    "ticket_authorization", default=None
)


def ticket_payload(summary: str, priority: str, asset_id: str) -> tuple[str, str, str]:
    return summary.strip(), priority.strip().lower(), asset_id.strip().upper()


def consume_ticket_authorization(payload: tuple[str, str, str]) -> bool:
    if _TICKET_AUTHORIZATION.get() != payload:
        return False
    _TICKET_AUTHORIZATION.set(None)
    return True


@dataclass
class TicketConfirmation:
    """Session-local draft; only a new, exact user reply can authorize it."""

    pending: tuple[str, str, str] | None = None
    approved: tuple[str, str, str] | None = None

    def begin_turn(self, user_text: str) -> None:
        reply = fold_text(user_text).replace("\u0111", "d").strip().rstrip(".!")
        self.approved = self.pending if reply in {
            "yes", "confirm", "i confirm", "dong y", "xac nhan", "toi xac nhan", "co"
        } else None
        # Any revision/cancellation/unrelated turn invalidates the earlier draft.
        self.pending = None

    @contextmanager
    def authorization(self):
        token = _TICKET_AUTHORIZATION.set(self.approved)
        self.approved = None
        try:
            yield
        finally:
            _TICKET_AUTHORIZATION.reset(token)

    def observe(self, result: Any) -> None:
        if isinstance(result, dict) and result.get("status") == "needs_confirmation":
            draft = result.get("draft")
            if isinstance(draft, dict):
                self.pending = ticket_payload(
                    draft["summary"], draft["priority"], draft["asset_id"]
                )


def split_reference_text(value: str) -> tuple[str, list[str]]:
    """Heuristic quarantine, not a claim that remaining text is trustworthy."""
    safe, removed = [], []
    instruction = re.compile(
        r"(?:system|developer|assistant|tro ly)\s*:|"
        r"ignore\s+(?:all|previous|the)|bo qua|tool_(?:calls|results)_json|"
        r"(?:call|invoke|execute|run|goi|chay)\s+.*"
        r"(?:create_ticket|shell_exec|curl|tool)|"
        r"(?:reveal|print|disclose).*(?:system prompt|hidden polic)|"
        r"confirmed\s*[:=]\s*true",
        re.IGNORECASE,
    )
    for line in str(value or "").splitlines():
        if line.strip().startswith(">") or instruction.search(fold_text(line)):
            removed.append(line.strip())
        else:
            safe.append(line)
    return "\n".join(safe).strip(), removed


def contains_sensitive_payload(value: str) -> bool:
    text = fold_text(value)
    label = r"(?:password|passwd|mat khau|token|api[ _-]?key|mfa|otp|recovery[ _-]?codes?|ma khoi phuc)"
    return bool(
        re.search(r"\b" + label + r"""[\x22\x27]?\s*(?:[:=]|is\b|la\b)\s*\S+""", text)
        or re.search(r"\b" + label + r"(?:\s+code)?\s+(?!(?:reset|change|expired|rotation|unavailable|required)\b)\S+", text)
        or re.search(r"\b(?:mfa|otp|recovery[ _-]?codes?|ma khoi phuc)\s+\S+", text)
        or re.search(r"\b(?:gsk_|sk-|sk_)[a-z0-9_-]{12,}\b", text)
    )
