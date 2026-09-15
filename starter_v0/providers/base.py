from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ModelResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any | None = None


class Provider(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        """Return normalized text/tool calls regardless of vendor API shape."""


class RateLimitedProvider:
    """Space model requests so one process does not exceed a configured RPM."""

    def __init__(self, provider: Provider, requests_per_minute: float = 15.0) -> None:
        if requests_per_minute < 0:
            raise ValueError("requests_per_minute must be zero or greater")
        self.provider = provider
        self.requests_per_minute = requests_per_minute
        self._minimum_interval = 60.0 / requests_per_minute if requests_per_minute else 0.0
        self._next_request_at = 0.0
        self._lock = threading.Lock()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.provider, name)

    def _wait_for_slot(self) -> None:
        if not self._minimum_interval:
            return
        with self._lock:
            now = time.monotonic()
            wait_seconds = self._next_request_at - now
            if wait_seconds > 0:
                time.sleep(wait_seconds)
                now = time.monotonic()
            self._next_request_at = now + self._minimum_interval

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        self._wait_for_slot()
        return self.provider.complete(
            messages,
            tools,
            model=model,
            temperature=temperature,
            tool_choice=tool_choice,
        )
