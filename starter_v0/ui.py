from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import (
    now_iso,
    safe_slug,
    trim_history,
    run_model_tool_loop,
    write_transcript,
)

load_lab_env(ROOT)

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IT Helpdesk Assistant — AI Agent Chat UI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    pre code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .chat-container { height: calc(100vh - 270px); }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">

  <!-- Top Navbar -->
  <header class="bg-slate-800 border-b border-slate-700 px-6 py-4 flex flex-wrap justify-between items-center shadow-lg">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow">
        <i class="fa-solid fa-headset text-xl"></i>
      </div>
      <div>
        <h1 class="font-bold text-lg text-white leading-tight">Northstar IT Helpdesk Assistant</h1>
        <p class="text-xs text-slate-400">Agentic Tool Calling Interface & Live Diagnostics</p>
      </div>
    </div>
    
    <!-- Badges & Controls -->
    <div class="flex items-center space-x-2 text-xs mt-2 sm:mt-0">
      <span class="bg-blue-900/60 text-blue-300 border border-blue-500/40 px-3 py-1.5 rounded-full font-mono font-medium">
        <i class="fa-solid fa-code-commit mr-1"></i> Version: <span id="badge-version">v3</span>
      </span>
      <span class="bg-emerald-900/60 text-emerald-300 border border-emerald-500/40 px-3 py-1.5 rounded-full font-mono font-medium">
        <i class="fa-solid fa-server mr-1"></i> Provider: <span id="badge-provider">openrouter</span>
      </span>
      <button onclick="resetChat()" class="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-600 transition flex items-center">
        <i class="fa-solid fa-rotate-right mr-1.5"></i> Reset
      </button>
      <button onclick="downloadTranscript()" class="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg shadow transition flex items-center">
        <i class="fa-solid fa-download mr-1.5"></i> Export Transcript
      </button>
    </div>
  </header>

  <!-- Quick Scenarios Helper -->
  <div class="bg-slate-800/60 border-b border-slate-700/80 px-6 py-2.5 flex items-center space-x-2 text-xs overflow-x-auto">
    <span class="text-slate-400 font-semibold uppercase tracking-wider whitespace-nowrap mr-1">
      <i class="fa-solid fa-bolt text-amber-400 mr-1"></i> Kịch bản mẫu:
    </span>
    <button onclick="fillPrompt('Kiểm tra trạng thái dịch vụ VPN trên môi trường production giúp mình.')" 
      class="bg-slate-700/80 hover:bg-slate-600 text-slate-200 px-2.5 py-1 rounded border border-slate-600 whitespace-nowrap transition">
      1. Yêu cầu bình thường (Check VPN)
    </button>
    <button onclick="fillPrompt('Máy laptop của mình bị lỗi màn hình, kiểm tra giúp mình với.')" 
      class="bg-slate-700/80 hover:bg-slate-600 text-slate-200 px-2.5 py-1 rounded border border-slate-600 whitespace-nowrap transition">
      2. Thiếu thông tin (Hỏi Asset ID)
    </button>
    <button onclick="fillPrompt('Kiểm tra máy LT-204 giúp mình.')" 
      class="bg-slate-700/80 hover:bg-slate-600 text-slate-200 px-2.5 py-1 rounded border border-slate-600 whitespace-nowrap transition">
      3. Nhiều lượt (Sửa sang LT-240)
    </button>
    <button onclick="fillPrompt('Tạo ticket mức high cho lỗi VPN trên máy LT-204 giúp mình.')" 
      class="bg-slate-700/80 hover:bg-slate-600 text-slate-200 px-2.5 py-1 rounded border border-slate-600 whitespace-nowrap transition">
      4. Tạo Ticket (Xin xác nhận)
    </button>
    <button onclick="fillPrompt('Kiểm tra thời hạn bảo hành và tình trạng vòng đời của thiết bị LT-204.')" 
      class="bg-amber-950/40 hover:bg-amber-900/60 text-amber-300 px-2.5 py-1 rounded border border-amber-600/40 whitespace-nowrap transition">
      ⭐ Bonus: Bảo hành (check_asset_warranty)
    </button>
  </div>

  <!-- Chat Messages Stream -->
  <main id="chat-stream" class="chat-container flex-1 overflow-y-auto px-6 py-6 space-y-6 max-w-5xl w-full mx-auto">
    <!-- Welcome message -->
    <div class="flex items-start space-x-3">
      <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm shrink-0 shadow">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-4 max-w-2xl text-sm shadow-md">
        <p class="font-semibold text-blue-400 mb-1">Trợ lý Northstar Labs IT Helpdesk</p>
        <p class="text-slate-300">
          Xin chào! Tôi có thể hỗ trợ bạn kiểm tra trạng thái dịch vụ (VPN, Email, SSO), chẩn đoán thiết bị (máy tính, máy in), tra cứu quy trình/chính sách và hỗ trợ mở ticket sự cố. Bạn cần hỗ trợ vấn đề gì hôm nay?
        </p>
      </div>
    </div>
  </main>

  <!-- Input Bar -->
  <footer class="bg-slate-800 border-t border-slate-700 p-4 shadow-inner">
    <div class="max-w-5xl mx-auto flex items-end space-x-3">
      <div class="flex-1 bg-slate-900 border border-slate-700 rounded-xl focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition px-3 py-2">
        <textarea id="user-input" rows="2" 
          placeholder="Nhập yêu cầu hỗ trợ kỹ thuật (Shift+Enter để xuống dòng)..." 
          class="w-full bg-transparent border-0 focus:outline-none text-slate-100 text-sm resize-none"
          onkeydown="handleKeyDown(event)"></textarea>
      </div>
      <button id="send-btn" onclick="sendMessage()" 
        class="bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-3 rounded-xl shadow transition flex items-center justify-center h-12">
        <i class="fa-solid fa-paper-plane mr-2"></i> Gửi
      </button>
    </div>
  </footer>

  <!-- Script Logic -->
  <script>
    let transcriptId = "";

    async function loadStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('badge-version').innerText = data.version || 'v3';
        document.getElementById('badge-provider').innerText = `${data.provider} (${data.model})`;
        transcriptId = data.transcript_id;
      } catch (err) {
        console.error("Failed to load server status:", err);
      }
    }

    function fillPrompt(text) {
      const input = document.getElementById('user-input');
      input.value = text;
      input.focus();
    }

    function handleKeyDown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    }

    function formatJSON(obj) {
      return JSON.stringify(obj, null, 2);
    }

    function appendUserMessage(text) {
      const stream = document.getElementById('chat-stream');
      const time = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const html = `
        <div class="flex items-start justify-end space-x-3">
          <div class="bg-blue-600 text-white rounded-2xl rounded-tr-none p-4 max-w-2xl text-sm shadow-md">
            <div class="flex justify-between items-center text-xs text-blue-200 mb-1">
              <span class="font-semibold">Bạn</span>
              <span>${time}</span>
            </div>
            <p class="whitespace-pre-wrap">${escapeHtml(text)}</p>
          </div>
          <div class="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-white text-sm shrink-0 shadow">
            <i class="fa-solid fa-user"></i>
          </div>
        </div>
      `;
      stream.insertAdjacentHTML('beforeend', html);
      stream.scrollTop = stream.scrollHeight;
    }

    function appendAssistantMessage(data) {
      const stream = document.getElementById('chat-stream');
      const time = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const text = data.assistant_text || "(Không có phản hồi văn bản)";
      const toolEvents = data.tool_events || [];

      let toolsHtml = "";
      if (toolEvents.length > 0) {
        toolsHtml = `
          <div class="mt-3 space-y-2 border-t border-slate-700/80 pt-3">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
              <i class="fa-solid fa-wrench mr-1.5 text-amber-400"></i> Các công cụ đã thực thi (${toolEvents.length}):
            </div>
        `;

        toolEvents.forEach((ev, idx) => {
          const isError = !!(ev.result && ev.result.error);
          const statusBadge = isError 
            ? `<span class="bg-rose-950 text-rose-300 border border-rose-600/40 text-[10px] px-2 py-0.5 rounded font-mono">ERROR</span>`
            : `<span class="bg-emerald-950 text-emerald-300 border border-emerald-600/40 text-[10px] px-2 py-0.5 rounded font-mono">SUCCESS</span>`;

          toolsHtml += `
            <div class="bg-slate-900/90 border border-slate-700 rounded-lg p-3 text-xs">
              <div class="flex justify-between items-center cursor-pointer select-none" onclick="toggleToolDetails('tool-box-${data.turn_index}-${idx}')">
                <div class="flex items-center space-x-2">
                  <span class="font-mono font-bold text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-700/30">
                    <i class="fa-solid fa-gear mr-1"></i>${escapeHtml(ev.tool)}
                  </span>
                  ${statusBadge}
                </div>
                <span class="text-slate-500 hover:text-slate-300 text-xs">
                  <i class="fa-solid fa-chevron-down" id="icon-tool-box-${data.turn_index}-${idx}"></i> Chi tiết
                </span>
              </div>

              <div id="tool-box-${data.turn_index}-${idx}" class="mt-2.5 pt-2.5 border-t border-slate-800 space-y-2">
                <div>
                  <span class="text-slate-400 font-semibold block mb-1">Tham số (Arguments):</span>
                  <pre class="bg-slate-950 p-2 rounded text-slate-300 overflow-x-auto"><code>${escapeHtml(formatJSON(ev.args))}</code></pre>
                </div>
                <div>
                  <span class="text-slate-400 font-semibold block mb-1">Kết quả / Lỗi (Result):</span>
                  <pre class="bg-slate-950 p-2 rounded ${isError ? 'text-rose-400' : 'text-emerald-300'} overflow-x-auto"><code>${escapeHtml(formatJSON(ev.result))}</code></pre>
                </div>
              </div>
            </div>
          `;
        });
        toolsHtml += `</div>`;
      }

      const html = `
        <div class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm shrink-0 shadow">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div class="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-4 max-w-3xl text-sm shadow-md w-full">
            <div class="flex justify-between items-center text-xs text-slate-400 mb-1.5">
              <span class="font-semibold text-blue-400">Agent Phản hồi (Lượt #${data.turn_index})</span>
              <span>${time}</span>
            </div>
            <div class="text-slate-200 whitespace-pre-wrap leading-relaxed">${escapeHtml(text)}</div>
            ${toolsHtml}
          </div>
        </div>
      `;
      stream.insertAdjacentHTML('beforeend', html);
      stream.scrollTop = stream.scrollHeight;
    }

    function toggleToolDetails(id) {
      const el = document.getElementById(id);
      if (el) {
        el.classList.toggle('hidden');
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    async function sendMessage() {
      const input = document.getElementById('user-input');
      const text = input.value.trim();
      if (!text) return;

      appendUserMessage(text);
      input.value = "";

      const btn = document.getElementById('send-btn');
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Đang xử lý...`;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_text: text })
        });
        const data = await res.json();
        appendAssistantMessage(data);
      } catch (err) {
        alert("Lỗi kết nối tới Agent API: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-paper-plane mr-2"></i> Gửi`;
      }
    }

    async function resetChat() {
      if (!confirm("Bạn có muốn làm mới phiên hội thoại và tạo transcript mới?")) return;
      try {
        await fetch('/api/reset', { method: 'POST' });
        document.getElementById('chat-stream').innerHTML = "";
        loadStatus();
      } catch (err) {
        alert("Lỗi reset: " + err.message);
      }
    }

    function downloadTranscript() {
      window.open('/api/transcript', '_blank');
    }

    window.onload = loadStatus;
  </script>
</body>
</html>
"""


class AgentUIServer:
    def __init__(
        self,
        *,
        provider_name: str,
        version_label: str,
        model: str | None = None,
        history_window: int = 5,
        max_tool_rounds: int = 4,
    ):
        self.provider_name = provider_name
        self.version_label = version_label
        self.system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        self.tools_path = ARTIFACTS_DIR / "tools.yaml"
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds

        self.system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
        self.tool_declarations = load_tool_declarations(self.tools_path)
        self.openai_tools = to_openai_tools(self.tool_declarations)
        self.provider = make_provider(provider_name)
        self.model = model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(version_label, self.system_prompt_path, self.tools_path)

        self.history: list[dict[str, str]] = []
        self.turn_index = 0
        self.init_transcript()

    def init_transcript(self) -> None:
        self.history = []
        self.turn_index = 0
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        self.transcript_id = "_".join([
            safe_slug(self.version_label),
            safe_slug(self.provider_name),
            timestamp,
        ])
        self.transcript_path = TRANSCRIPTS_DIR / f"{self.transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": self.provider_name,
            "model": self.model,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        write_transcript(self.transcript_path, self.transcript)

    def process_turn(self, user_text: str) -> dict[str, Any]:
        self.turn_index += 1
        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.history_window),
            {"role": "user", "content": user_text},
        ]

        turn_record: dict[str, Any] = {
            "turn_index": self.turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            result = run_model_tool_loop(
                provider=self.provider,
                messages=messages,
                tools=self.openai_tools,
                model=self.model,
                max_tool_rounds=self.max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
                "assistant_text": f"Lỗi thực thi Provider: {exc}",
            })

        turn_record["ended_at"] = now_iso()
        self.transcript["turns"].append(turn_record)
        write_transcript(self.transcript_path, self.transcript)

        return {
            "turn_index": self.turn_index,
            "assistant_text": turn_record["assistant_text"],
            "tool_events": turn_record.get("tool_events", []),
            "status": turn_record.get("status"),
            "transcript_id": self.transcript_id,
        }


def make_handler(agent_server: AgentUIServer):
    class UIHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/" or parsed.path == "/index.html":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_PAGE.encode("utf-8"))
            elif parsed.path == "/api/status":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                data = {
                    "version": agent_server.artifact_version.artifact_version,
                    "provider": agent_server.provider_name,
                    "model": agent_server.model,
                    "transcript_id": agent_server.transcript_id,
                }
                self.wfile.write(json.dumps(data).encode("utf-8"))
            elif parsed.path == "/api/transcript":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{agent_server.transcript_id}.json"')
                self.end_headers()
                self.wfile.write(json.dumps(agent_server.transcript, indent=2, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/chat":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                user_text = body.get("user_text", "").strip()

                resp = agent_server.process_turn(user_text)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
            elif parsed.path == "/api/reset":
                agent_server.init_transcript()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress normal noise
            pass

    return UIHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Web UI for IT Helpdesk Agent with Tool Calling diagnostics.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], default="openrouter")
    parser.add_argument("--version", default="v3")
    parser.add_argument("--model", default=None)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server_core = AgentUIServer(
        provider_name=args.provider,
        version_label=args.version,
        model=args.model,
    )

    handler_cls = make_handler(server_core)
    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), handler_cls)
    print(f"\n=======================================================")
    print(f"🚀 IT Helpdesk Web UI running on http://127.0.0.1:{args.port}")
    print(f"Artifact Version: {server_core.artifact_version.artifact_version}")
    print(f"Provider: {server_core.provider_name} | Model: {server_core.model}")
    print(f"Transcript logging to: {server_core.transcript_path}")
    print(f"=======================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
