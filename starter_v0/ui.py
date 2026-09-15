import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import os

# Import from existing chat.py logic
from chat import (
    run_model_tool_loop, trim_history, write_transcript, now_iso, safe_slug,
    ARTIFACTS_DIR, ROOT
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict
from env_loader import load_lab_env

# Load environment variables just like chat.py does
load_lab_env(ROOT)

st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🤖", layout="centered")

st.title("🤖 IT Helpdesk Agent")
st.markdown("Giao diện Chat thông minh tích hợp Tool Calling")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Cấu hình (Settings)")
    provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini"])
    version = st.selectbox("Version", ["v0", "v1", "v2", "v3"])
    model_name = st.text_input("Model (để trống để dùng mặc định)", value="")
    max_tool_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)
    
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử Chat"):
        st.session_state.clear()
        st.rerun()

# --- INITIALIZE SESSION STATE ---
# If settings change or app just loaded, initialize/reset history and transcript
if (
    "transcript" not in st.session_state 
    or st.session_state.get("last_version") != version 
    or st.session_state.get("last_provider") != provider_name
):
    st.session_state.history = []
    st.session_state.turn_index = 0
    st.session_state.last_version = version
    st.session_state.last_provider = provider_name
    
    # Init transcript
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    
    st.session_state.transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    
    st.toast("Đã khởi tạo phiên chat mới!", icon="✅")

# --- DISPLAY CHAT HISTORY ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display tool events if they exist in this history turn
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander(f"🛠️ Đã dùng {len(msg['tool_events'])} công cụ (Click để xem chi tiết)"):
                for event in msg["tool_events"]:
                    st.write(f"**Tool:** `{event['tool']}`")
                    st.json(event['args'])
                    st.write("**Kết quả:**")
                    st.json(event['result'])

# --- HANDLE USER INPUT ---
user_input = st.chat_input("Nhập yêu cầu của bạn (VD: LT-204 đang bị lỗi gì?)")

if user_input:
    # 1. Show user message instantly
    with st.chat_message("user"):
        st.markdown(user_input)
        
    st.session_state.turn_index += 1
    
    # Prepare backend dependencies
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    
    try:
        provider = make_provider(provider_name)
    except Exception as e:
        st.error(f"Lỗi khởi tạo Provider: {str(e)}")
        st.stop()
        
    # Construct context window
    # We only take the text content for the model context, ignoring the UI-specific 'tool_events' key
    pure_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(pure_history, 5),
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
    
    # 2. Call the Agent and show Spinner
    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích và gọi công cụ..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model_name if model_name else getattr(provider, "default_model", None),
                    max_tool_rounds=max_tool_rounds,
                )
                
                tool_events = result.get("tool_events", [])
                
                # Render tool calls beautifully using expander
                if tool_events:
                    with st.expander(f"🛠️ Đã dùng {len(tool_events)} công cụ (Click để xem chi tiết)", expanded=True):
                        for event in tool_events:
                            st.write(f"**Tool:** `{event['tool']}`")
                            st.json(event['args'])
                            st.write("**Kết quả:**")
                            st.json(event['result'])
                            
                # Output final response
                assistant_text = result.get("assistant_text", "")
                st.markdown(assistant_text)
                
                # Save to session history (including tool_events for rendering later)
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({
                    "role": "assistant", 
                    "content": assistant_text,
                    "tool_events": tool_events
                })
                
                # Update record for transcript
                turn_record.update(result)
                
            except Exception as exc:
                st.error(f"Lỗi Provider: {str(exc)}")
                turn_record.update({
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {str(exc)}",
                })
        
        # 3. Save transcript to JSON file silently
        turn_record["ended_at"] = now_iso()
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
