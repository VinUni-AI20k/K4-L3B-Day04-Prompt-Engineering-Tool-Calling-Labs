import streamlit as st
import json
from pathlib import Path

# Tái sử dụng code có sẵn từ file chat.py và hệ thống của bạn
from chat import run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

# 1. Tải cấu hình 1 lần duy nhất để tối ưu hiệu năng
@st.cache_resource

def format_display_text(text):
    if not text:
        return "Không có câu trả lời."
    try:
        # Cố gắng đọc văn bản dưới dạng JSON
        data = json.loads(text)
        if isinstance(data, dict) and "reply" in data:
            return data["reply"] # Chỉ lấy phần reply để hiển thị
    except Exception:
        pass # Nếu không phải JSON hợp lệ, bỏ qua
    
    return text # Trả về văn bản gốc nếu nó không có định dạng JSON

def load_setup():
    ROOT = Path(__file__).parent
    # Lấy system prompt và tools giống hệt cách chat.py làm
    system_prompt = (ROOT / "artifacts" / "system_prompt.md").read_text(encoding="utf-8")
    tools_yaml = ROOT / "artifacts" / "tools.yaml"
    openai_tools = to_openai_tools(load_tool_declarations(tools_yaml))
    
    # Khởi tạo provider (ở đây mặc định dùng openrouter)
    provider = make_provider("gemini") 
    return system_prompt, openai_tools, provider

st.title("🎧 IT Helpdesk Agent")
with st.sidebar:
    st.markdown("### ℹ️ Thông tin hệ thống")
    st.info("Phiên bản Artifact: v0")
    st.success("Provider: Gemini")
system_prompt, openai_tools, provider = load_setup()

# 2. Khởi tạo bộ nhớ tạm (Session State) để lưu lịch sử chat trên web
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Hiển thị lại toàn bộ lịch sử chat mỗi khi web reload
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tool_events"):
            for event in msg["tool_events"]:
                with st.expander(f"🛠️ Đã gọi tool: {event.get('tool')}"):
                    st.write("**Tham số (Input):**")
                    st.json(event.get("args", {}))
                    st.write("**Kết quả / Lỗi:**")
                    st.json(event.get("result", {}))
        st.markdown(format_display_text(msg["content"]))

# 4. Bắt sự kiện khi người dùng gõ tin nhắn và Enter
if prompt := st.chat_input("Nhập vấn đề IT của bạn vào đây..."):
    # Hiển thị tin nhắn của người dùng lên web ngay lập tức
    st.chat_message("user").markdown(prompt)

    # Chuẩn bị context để nạp vào model giống trong chat.py
    model_messages = [{"role": "system", "content": system_prompt}]
    model_messages.extend(trim_history(st.session_state.messages, window=5))
    model_messages.append({"role": "user", "content": prompt})

    # Gọi Bot và hiển thị loading...
    with st.chat_message("assistant"):
        with st.spinner("Đang kiểm tra hệ thống và suy nghĩ..."):
            try:
                # Sử dụng lại đúng vòng lặp xử lý tool của bạn
                result = run_model_tool_loop(
                    provider=provider,
                    messages=model_messages,
                    tools=openai_tools,
                    model="gemini-3.1-flash-lite", 
                    max_tool_rounds=4
                )
                assistant_text = result.get("assistant_text", "Không có câu trả lời.")
                tool_events = result.get("tool_events", [])

                for event in tool_events:
                    with st.expander(f"🛠️ Đã gọi tool: {event.get('tool')}"):
                        st.write("**Tham số (Input):**")
                        st.json(event.get("args", {}))
                        st.write("**Kết quả / Lỗi:**")
                        st.json(event.get("result", {}))

                st.markdown(format_display_text(assistant_text))
                
                # Lưu vào lịch sử để duy trì ngữ cảnh
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_text,
                    "tool_events": tool_events # Lưu thêm trường này
                })
                
            except Exception as e:
                st.error(f"Lỗi kết nối Provider: {str(e)}")