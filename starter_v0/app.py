import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, write_transcript, trim_history, safe_slug, now_iso

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🤖", layout="wide")

st.title("IT Helpdesk Agent 🤖")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    version = st.selectbox("Version", ["v0", "v1", "v2", "v3"], index=3)
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    
    st.markdown("---")
    st.markdown("**Transcript File:**")
    if "transcript_path" in st.session_state:
        st.code(str(st.session_state.transcript_path))

# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_index" not in st.session_state:
    st.session_state.turn_index = 0

# Load configurations
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)
provider = make_provider(provider_name)
artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

if "transcript" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    transcripts_dir = ROOT / "transcripts"
    transcript_path = transcripts_dir / f"{transcript_id}.transcript.json"
    
    st.session_state.transcript_path = transcript_path
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": getattr(provider, "default_model", None),
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            for event in msg["tool_events"]:
                with st.expander(f"🔧 Tool Call: {event['tool']}"):
                    st.json({"args": event["args"], "result": event["result"]})

# Chat input
if user_input := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    st.session_state.turn_index += 1
    
    messages_payload = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_input},
    ]
    
    turn_record = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_input,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages_payload,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=4,
                )
                
                turn_record.update(result)
                assistant_text = result["assistant_text"]
                tool_events = result.get("tool_events", [])
                
                st.markdown(assistant_text)
                
                for event in tool_events:
                    with st.expander(f"🔧 Tool Call: {event['tool']}"):
                        st.json({"args": event["args"], "result": event["result"]})
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_text,
                    "tool_events": tool_events
                })
                
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
            except Exception as exc:
                error_msg = f"{type(exc).__name__}: {str(exc)}"
                turn_record.update({"status": "provider_error", "error": error_msg})
                st.error(error_msg)
                
    # Save transcript
    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
