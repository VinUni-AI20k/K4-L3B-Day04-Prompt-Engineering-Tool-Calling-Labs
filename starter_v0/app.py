from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


TRANSCRIPTS_DIR = ROOT / "transcripts"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def initialise_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "transcript_path" not in st.session_state:
        st.session_state.transcript_path = None


def reset_chat() -> None:
    st.session_state.history = []
    st.session_state.messages = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None


def start_transcript(
    artifact: Any,
    provider_name: str,
    model: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"ui_{artifact.version}_{provider_name}_{timestamp}"
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript_path = path
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_tool_event(event: dict[str, Any], index: int) -> None:
    result = event.get("result", {})
    label = f"{event.get('tool', 'unknown')}  ·  event {index}"
    with st.expander(label, expanded=False):
        st.caption("Tool input / arguments")
        st.json(event.get("args", {}))
        st.caption("Tool result or error")
        st.json(result)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Nunito:wght@700;800&display=swap');

        :root {
            --cream: #fffaf4;
            --ink: #263238;
            --muted: #6f7b78;
            --coral: #ef7d6d;
            --coral-dark: #d85f55;
            --mint: #dff3e8;
            --mint-dark: #26735c;
            --line: #f0e4d8;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 92% 4%, rgba(239, 125, 109, .12) 0 120px, transparent 121px),
                radial-gradient(circle at 4% 82%, rgba(136, 203, 173, .13) 0 150px, transparent 151px),
                var(--cream);
            color: var(--ink);
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stMainBlockContainer"] { max-width: 1120px; padding-top: 2.5rem; }
        [data-testid="stSidebar"] {
            background: #fff3e8;
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: var(--ink); }

        h1, h2, h3 { font-family: 'Nunito', 'Trebuchet MS', sans-serif !important; color: var(--ink); }
        h1 { letter-spacing: 0; font-size: 2.55rem !important; margin-bottom: .15rem !important; }
        p, label, [data-testid="stCaptionContainer"] { font-family: 'DM Sans', sans-serif; }
        [data-testid="stCaptionContainer"] { color: var(--muted); }

        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stChatMessage"]) {
            animation: rise-in .35s ease-out both;
        }
        [data-testid="stChatMessage"] {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: .8rem 1rem;
            margin: .7rem 0;
            box-shadow: 0 8px 22px rgba(86, 67, 52, .05);
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #fff1e9;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: #f0faf4;
        }
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
            font-family: 'DM Sans', sans-serif;
            color: var(--ink);
        }
        [data-testid="stChatInput"] {
            border: 2px solid #f3d7c6;
            border-radius: 18px;
            background: rgba(255, 255, 255, .9);
            box-shadow: 0 10px 28px rgba(86, 67, 52, .08);
        }
        [data-testid="stChatInput"]:focus-within { border-color: var(--coral); }
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
            border-radius: 12px;
            border-color: #efd9c9;
            background: #fffdfb;
        }
        .stButton > button, [data-testid="stDownloadButton"] button {
            border: 0;
            border-radius: 12px;
            background: var(--coral);
            color: white;
            font-family: 'DM Sans', sans-serif;
            font-weight: 700;
            transition: transform .15s ease, background .15s ease;
        }
        .stButton > button:hover, [data-testid="stDownloadButton"] button:hover {
            background: var(--coral-dark);
            color: white;
            transform: translateY(-1px);
        }
        [data-testid="stExpander"] {
            border: 1px solid #d6eadf;
            border-radius: 14px;
            background: rgba(255, 255, 255, .65);
        }
        [data-testid="stExpander"] summary { color: var(--mint-dark); font-weight: 700; }
        hr { border-color: var(--line); }

        @keyframes rise-in {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Agent", page_icon=":material/support_agent:", layout="wide")
    load_lab_env(ROOT)
    initialise_state()
    apply_theme()

    st.markdown("<div style='font-size:.82rem;color:#d85f55;font-weight:700;letter-spacing:.08em;text-transform:uppercase;'>IT support corner</div>", unsafe_allow_html=True)
    st.title("IT Helpdesk Agent")
    st.caption("A small, friendly place to untangle your tech troubles.")

    with st.sidebar:
        st.header("Run settings")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
        version = st.text_input("Artifact version", value="ui")
        model = st.text_input("Model override", value="", help="Leave blank to use the provider default.") or None
        history_window = st.number_input("History pairs", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)
        st.divider()
        artifact = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")
        st.caption(f"Artifact: `{artifact.artifact_version}`")
        if st.button("Reset conversation", use_container_width=True):
            reset_chat()
            st.rerun()

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(declarations)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            for index, event in enumerate(message.get("tool_events", []), start=1):
                render_tool_event(event, index)

    prompt = st.chat_input("Describe your IT issue...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt, "tool_events": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is checking the request..."):
            try:
                provider = make_provider(provider_name)
                selected_model = model or getattr(provider, "default_model", None)
                if st.session_state.transcript is None:
                    st.session_state.transcript = start_transcript(
                        artifact,
                        provider_name,
                        selected_model,
                        int(history_window),
                        int(max_tool_rounds),
                    )

                messages = [
                    {"role": "system", "content": system_prompt},
                    *trim_history(st.session_state.history, int(history_window)),
                    {"role": "user", "content": prompt},
                ]
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=int(max_tool_rounds),
                )
                assistant_text = result["assistant_text"]
                st.markdown(assistant_text)
                for index, event in enumerate(result["tool_events"], start=1):
                    render_tool_event(event, index)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": result["tool_events"],
                    "status": result["status"],
                })
                st.session_state.history.extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": assistant_text},
                ])
                st.session_state.transcript["turns"].append({
                    "turn_index": len(st.session_state.transcript["turns"]) + 1,
                    "started_at": now_iso(),
                    "ended_at": now_iso(),
                    "user": prompt,
                    **result,
                })
                write_transcript(st.session_state.transcript_path, st.session_state.transcript)
            except Exception as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                st.error(error_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_text,
                    "tool_events": [],
                    "status": "provider_error",
                })

    if st.session_state.transcript_path:
        transcript_json = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
        st.sidebar.download_button(
            "Download transcript",
            data=transcript_json,
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )
        st.sidebar.caption(f"Saved: `{st.session_state.transcript_path}`")


if __name__ == "__main__":
    main()