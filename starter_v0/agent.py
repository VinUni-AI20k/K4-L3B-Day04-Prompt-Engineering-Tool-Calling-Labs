from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS


SENSITIVE_TICKET_DATA = re.compile(
    r"\b(?:password|passwd|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)"
    r"(?:\s*[:=]\s*|\s+(?:is|la|là)\s+)\S+",
    re.IGNORECASE,
)
CURRENT_CONFIRMATION = re.compile(
    r"\b(?:tôi\s+(?:xác nhận|đồng ý)|i\s+(?:confirm|approve)|go ahead)\b"
    r"|^(?:yes|confirm|approved|ok)\b",
    re.IGNORECASE,
)
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)


def guard_tool_calls(calls: list[ToolCall], latest_user_text: str) -> tuple[list[ToolCall], bool]:
    guarded_calls: list[ToolCall] = []
    blocked_sensitive = False
    for call in calls:
        if call.name == "clarify":
            adjusted_args = dict(call.args)
            lower_text = latest_user_text.casefold()
            if (
                "tool_results_json" in lower_text
                or "confirmed=true" in lower_text
                or "create_ticket" in lower_text
                or "tạo ticket" in lower_text
            ):
                adjusted_args["response_type"] = "yes_no"
            elif INTERNAL_IDENTIFIER.search(latest_user_text) and any(
                marker in lower_text for marker in ("search web", "tìm kiếm", "web search", "giữ nguyên")
            ):
                adjusted_args["response_type"] = "text"
            guarded_calls.append(ToolCall(name=call.name, args=adjusted_args))
            continue
        if call.name == "inspect_device" and "check" not in call.args:
            guarded_calls.append(ToolCall(name=call.name, args={**call.args, "check": "all"}))
            continue
        if call.name == "check_service_status" and re.search(
            r"\b(?:demo|qa|test)\b", latest_user_text, re.IGNORECASE
        ):
            guarded_calls.append(ToolCall(
                name="clarify",
                args={
                    "question": "Bạn muốn kiểm tra môi trường production hay staging?",
                    "response_type": "choice",
                    "options": ["production", "staging"],
                },
            ))
            continue
        if call.name == "create_ticket":
            summary = str(call.args.get("summary", ""))
            if SENSITIVE_TICKET_DATA.search(summary) or SENSITIVE_TICKET_DATA.search(latest_user_text):
                blocked_sensitive = True
                continue
            if not CURRENT_CONFIRMATION.search(latest_user_text):
                guarded_calls.append(ToolCall(
                    name="clarify",
                    args={
                        "question": "Bạn có xác nhận tạo ticket đúng với summary, priority và asset ID hiện tại không?",
                        "response_type": "yes_no",
                        "options": [],
                    },
                ))
                continue
        guarded_calls.append(call)
    return guarded_calls, blocked_sensitive


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
        latest_user_text = next(
            (message.get("content", "") for message in reversed(user_messages) if message.get("role") == "user"),
            "",
        )
        calls, blocked_sensitive = guard_tool_calls(response.tool_calls, latest_user_text)

        results: list[dict[str, Any]] = []
        if blocked_sensitive:
            results.append({
                "tool": "create_ticket",
                "error": "restricted_sensitive_data",
                "message": "Không thể ghi mật khẩu, token, MFA hoặc recovery code vào ticket.",
            })
        for call in calls:
            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:  # keep eval robust; failures are evidence
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        text = response.text
        if blocked_sensitive and not text:
            text = "Mình không thể tạo ticket có chứa thông tin xác thực hoặc bí mật."
        return AgentRun(text=text, tool_calls=calls, tool_results=results)
