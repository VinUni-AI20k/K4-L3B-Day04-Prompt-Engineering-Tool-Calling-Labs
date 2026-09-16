from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
load_lab_env(ROOT)

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_declarations)
artifact_version = build_artifact_version("v3", SYSTEM_PROMPT_PATH, TOOLS_PATH)

st.set_page_config(page_title="Northstar Service Desk", page_icon="N", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
    :root { --ink:#17202a; --muted:#68737d; --paper:#f5f7f5; --line:#d8dfdc; --teal:#0e716d; --coral:#d45d43; }
    .stApp { background:var(--paper); color:var(--ink); }
    [data-testid="stSidebar"] { background:#102e35; border-right:0; }
    [data-testid="stSidebar"] * { color:#e8f2ef; }
    .brand { padding:12px 0 24px; }
    .brand-mark { display:inline-flex; width:40px; height:40px; align-items:center; justify-content:center; border:1px solid #79c5ba; color:#b9efe3; font-weight:800; letter-spacing:1px; margin-right:10px; }
    .brand-name { display:inline-block; vertical-align:middle; font:800 18px/1.1 Manrope,sans-serif; color:#fff; }
    .brand-sub { display:block; margin:8px 0 0 52px; color:#9eb8b3; font:11px Manrope,sans-serif; letter-spacing:1.5px; text-transform:uppercase; }
    h1,h2,h3,p,span,div { font-family:Manrope,sans-serif; }
    code,pre { font-family:'DM Mono',monospace !important; }
    .eyebrow { color:var(--teal); font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; }
    .hero { border-bottom:1px solid var(--line); padding:8px 0 22px; margin-bottom:20px; }
    .hero h1 { font-size:34px; letter-spacing:-1px; margin:5px 0 0; }
    .hero p { color:var(--muted); margin:7px 0 0; }
    .stat { background:#fff; border:1px solid var(--line); padding:14px 16px; min-height:82px; }
    .stat-label { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:1.2px; }
    .stat-value { font-size:24px; font-weight:800; margin-top:5px; }
    .trace-card { background:#fff; border:1px solid var(--line); border-left:4px solid var(--teal); padding:14px 16px; margin:10px 0; }
    .trace-card.error { border-left-color:var(--coral); background:#fff8f6; }
    .trace-kicker { color:var(--muted); font-size:11px; font-weight:800; letter-spacing:1.2px; text-transform:uppercase; }
    .trace-title { font-size:17px; font-weight:800; margin-top:4px; }
    .stButton > button, .stDownloadButton > button { border-radius:2px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def init_state() -> None:
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_started", now_iso())


def is_error(value: Any) -> bool:
    return isinstance(value, dict) and bool(value.get("error"))


def all_events() -> list[dict[str, Any]]:
    return [event for turn in st.session_state.turns for event in turn.get("tool_events", [])]


def transcript_payload() -> dict[str, Any]:
    return {
        "transcript_type": "northstar_helpdesk_evidence",
        "transcript_version": "1.0",
        "session_started": st.session_state.session_started,
        "updated_at": now_iso(),
        "artifact": artifact_version_dict(artifact_version),
        "provider": "openrouter",
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools_declaration": str(TOOLS_PATH),
        "turns": st.session_state.turns,
    }


def transcript_markdown() -> str:
    lines = [
        "# Northstar Service Desk Transcript",
        f"- Session started: {st.session_state.session_started}",
        f"- Updated: {now_iso()}",
        f"- Artifact: `{artifact_version.artifact_version}`",
        "",
    ]
    for turn in st.session_state.turns:
        lines += [f"## Turn {turn['turn_index']} - {turn['status']}", "", f"**User request**\n\n{turn['user']}", ""]
        for round_record in turn.get("rounds", []):
            lines.append(f"### Tool round {round_record['round']}")
            for call, event in zip(round_record.get("tool_calls", []), round_record.get("tool_results", [])):
                result = event.get("result", {})
                lines += [
                    f"- **Tool:** `{call['name']}`",
                    f"- **Arguments:** `{json.dumps(call.get('args', {}), ensure_ascii=False)}`",
                    f"- **Result:** `{json.dumps(result, ensure_ascii=False)}`",
                ]
                if is_error(result):
                    lines.append("- **TOOL ERROR:** this execution returned an error.")
            lines.append("")
        lines += [f"**Assistant response**\n\n{turn.get('assistant_text') or '(no response)'}", ""]
    return "\n".join(lines)


def render_event(event: dict[str, Any], index: int) -> None:
    result = event.get("result", {})
    failed = is_error(result)
    label = "TOOL ERROR" if failed else "TOOL RESULT"
    css_class = "error" if failed else ""
    st.markdown(
        f"<div class='trace-card {css_class}'><div class='trace-kicker'>Evidence {index:02d} - {label}</div><div class='trace-title'>{event.get('tool', 'unknown_tool')}</div></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.caption("INPUT / ARGUMENTS")
        st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
    with right:
        st.caption("EXECUTION RESULT")
        if failed:
            st.error(json.dumps(result, ensure_ascii=False, indent=2), icon="!")
        else:
            st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")


def render_turn(turn: dict[str, Any]) -> None:
    failed = any(is_error(event.get("result")) for event in turn.get("tool_events", []))
    status = "TOOL FAILURE" if failed else turn.get("status", "completed").replace("_", " ").upper()
    st.markdown(f"### Turn {turn['turn_index']} - {status}")
    st.markdown(f"**User request**  \n{turn['user']}")
    if turn.get("error"):
        st.error(json.dumps(turn["error"], ensure_ascii=False, indent=2), icon="!")
    if not turn.get("tool_events"):
        st.info("No tool was called for this request.")
    else:
        for index, event in enumerate(turn["tool_events"], start=1):
            render_event(event, index)
    if turn.get("assistant_text"):
        st.markdown("**Assistant response**")
        st.markdown(turn["assistant_text"])
    st.divider()


init_state()

with st.sidebar:
    st.markdown(
        "<div class='brand'><span class='brand-mark'>NS</span><span class='brand-name'>Northstar<br>Service Desk</span><span class='brand-sub'>Evidence console</span></div>",
        unsafe_allow_html=True,
    )
    st.caption("A live helpdesk workspace where every answer stays attached to its evidence.")
    st.divider()
    st.markdown("**SESSION CONTROL**")
    st.caption(f"Started {st.session_state.session_started}")
    if st.button("Clear current session", use_container_width=True):
        st.session_state.turns = []
        st.session_state.messages = []
        st.session_state.session_started = now_iso()
        st.rerun()
    st.divider()
    st.markdown("**ACTIVE ARTIFACT**")
    st.code(artifact_version.artifact_version, language="text")

st.markdown(
    "<div class='hero'><div class='eyebrow'>Northstar Labs / Internal IT</div><h1>Helpdesk command center</h1><p>Ask for a diagnosis, policy lookup, or service check. The evidence trail stays visible.</p></div>",
    unsafe_allow_html=True,
)

events = all_events()
errors = sum(1 for event in events if is_error(event.get("result")))
stats = st.columns(4)
for column, label, value in zip(stats, ["Requests", "Tool calls", "Tool errors", "Evidence coverage"], [len(st.session_state.turns), len(events), errors, "100%" if st.session_state.turns else "--"]):
    with column:
        st.markdown(f"<div class='stat'><div class='stat-label'>{label}</div><div class='stat-value'>{value}</div></div>", unsafe_allow_html=True)

st.caption("Transcript view: every request is followed by exact tool input and execution output. A tool error is evidence, not a successful completion.")
for turn in st.session_state.turns:
    render_turn(turn)
if not st.session_state.turns:
    st.info("No requests in this session yet. Start with a service status question or an asset ID.")

with st.expander("Export transcript", expanded=False):
    st.caption("JSON is suited to evaluation; Markdown is suited to incident review.")
    payload = transcript_payload()
    download_json, download_markdown = st.columns(2)
    with download_json:
        st.download_button("Download evidence JSON", json.dumps(payload, ensure_ascii=False, indent=2), "northstar-transcript.json", "application/json", use_container_width=True)
    with download_markdown:
        st.download_button("Download report Markdown", transcript_markdown(), "northstar-transcript.md", "text/markdown", use_container_width=True)

if prompt := st.chat_input("Describe the IT issue or ask for a service check..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    chat_history = [{"role": "system", "content": system_prompt}, *st.session_state.messages]
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Routing request and collecting evidence..."):
            try:
                result = run_model_tool_loop(
                    provider=make_provider("openrouter"),
                    messages=chat_history,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=4,
                )
                turn = {
                    "turn_index": len(st.session_state.turns) + 1,
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                    "user": prompt,
                    "status": result.get("status", "answered"),
                    "assistant_text": result.get("assistant_text", ""),
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                }
                st.session_state.turns.append(turn)
                st.session_state.messages.append({"role": "assistant", "content": turn["assistant_text"]})
                st.rerun()
            except Exception as exc:
                error = {"type": type(exc).__name__, "message": str(exc)}
                turn = {
                    "turn_index": len(st.session_state.turns) + 1,
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                    "user": prompt,
                    "status": "provider_error",
                    "assistant_text": "The provider failed before a final answer was produced.",
                    "rounds": [],
                    "tool_events": [],
                    "error": error,
                }
                st.session_state.turns.append(turn)
                st.error(json.dumps(error, ensure_ascii=False, indent=2), icon="!")
