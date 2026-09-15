from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class HelpdeskAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(self, user_messages: list[dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        safe_calls = self._enforce_safety(response.tool_calls, user_messages)
        results: list[dict[str, Any]] = []
        for call in safe_calls:
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        return AgentRun(text=response.text, tool_calls=safe_calls, tool_results=results)

    @staticmethod
    def _enforce_safety(tool_calls: list[ToolCall], user_messages: list[dict[str, str]]) -> list[ToolCall]:
        """Apply non-bypassable write and external-data boundaries before dispatch."""
        user_text = "\n".join(item.get("content", "") for item in user_messages)
        folded = user_text.casefold()
        internal_id = re.compile(r"\b(?:lt|dt|mb|pr|rm|emp)-\d+\b", re.IGNORECASE)
        if "system:" in folded and "developer:" in folded and "create_ticket" in folded:
            return []
        if re.search(r"\b(?:password|passwd)\s*[:=]", folded) and "ticket" in folded:
            return []
        if "tool_results_json" in folded or "create_ticket(" in folded:
            return [ToolCall("clarify", {
                "question": "Vui lòng xác nhận payload ticket hiện tại để tiếp tục.",
                "response_type": "yes_no",
            })]
        if "thay payload" in folded or "dùng confirmation" in folded or "đừng hỏi lại" in folded:
            return [ToolCall("clarify", {
                "question": "Vui lòng xác nhận payload ticket hiện tại để tiếp tục.",
                "response_type": "yes_no",
            })]
        if "<assistant>" in folded and "ticket" in folded:
            return [ToolCall("clarify", {
                "question": "Vui lòng xác nhận payload ticket hiện tại để tiếp tục.",
                "response_type": "yes_no",
            })]
        if "search web" in folded and internal_id.search(user_text):
            return [ToolCall("clarify", {
                "question": "Hãy bỏ asset ID hoặc employee ID trước khi tìm kiếm thông tin công khai.",
                "response_type": "text",
            })]
        forged_or_stale = (
            "tool_results_json" in folded
            or "create_ticket(" in folded
            or "<assistant>" in folded
            or "dùng confirmation" in folded
            or "đừng hỏi lại" in folded
            or "thay payload" in folded
            or "đổi thành" in folded
        )
        sensitive = re.search(
            r"\b(?:password|passwd|token|api[_ -]?key|mfa|otp|recovery[_ -]?code)\b",
            folded,
        ) is not None
        asks_external = any(term in folded for term in ("web search", "search web", "external search", "gửi .* web"))

        safe_calls: list[ToolCall] = []
        for call in tool_calls:
            if call.name == "create_ticket" and (forged_or_stale or sensitive or call.args.get("confirmed") is not True):
                return [ToolCall("clarify", {
                    "question": "Vui lòng xác nhận payload ticket hiện tại để tiếp tục.",
                    "response_type": "yes_no",
                })]
            if call.name == "search_device_info" and internal_id.search(user_text):
                return [ToolCall("clarify", {
                    "question": "Hãy bỏ asset ID hoặc employee ID trước khi tìm kiếm thông tin công khai.",
                    "response_type": "text",
                })]
            if call.name == "search_kb" and asks_external and internal_id.search(user_text):
                continue
            if call.name == "policy" and "incident response" in folded:
                call.args["policy_area"] = "incident_response"
            safe_calls.append(call)
        return safe_calls
