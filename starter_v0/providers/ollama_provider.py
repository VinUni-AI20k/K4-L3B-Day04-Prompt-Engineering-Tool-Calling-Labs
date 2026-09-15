from __future__ import annotations

import json
from typing import Any

from providers.base import ModelResponse, ToolCall


class OllamaProvider:
    """Ollama provider using the OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434/v1",
        default_model: str = "qwen2.5:1.5b",
    ) -> None:
        self.base_url = base_url
        self.default_model = default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Install live provider dependency first: pip install openai"
            ) from exc

        client = OpenAI(
            api_key="ollama",
            base_url=self.base_url,
        )

        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            kwargs["tools"] = tools

        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        resp = client.chat.completions.create(**kwargs)

        msg = resp.choices[0].message

        calls: list[ToolCall] = []

        for call in msg.tool_calls or []:
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            calls.append(
                ToolCall(
                    name=call.function.name,
                    args=args,
                )
            )

        return ModelResponse(
            text=msg.content,
            tool_calls=calls,
            raw=resp,
        )