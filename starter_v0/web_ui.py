from __future__ import annotations

import argparse
import json
import threading
import time
import unicodedata
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    execute_tool_call,
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


load_lab_env(ROOT)

HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Northstar Helpdesk</title>
<style>
:root { --ink:#18212b; --muted:#68717b; --line:#dce2e7; --paper:#f4f7f8; --panel:#fff; --navy:#17324d; --teal:#087f78; --amber:#f0a43c; --red:#b84a4a; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:linear-gradient(135deg,#eef4f2 0%,#f8f5ef 55%,#e9eff4 100%); font-family:Georgia, 'Times New Roman', serif; min-height:100vh; }
button, textarea { font:inherit; }
button { cursor:pointer; }
.shell { max-width:1240px; margin:0 auto; padding:28px 22px 36px; }
.topbar { display:flex; justify-content:space-between; align-items:flex-start; gap:24px; margin-bottom:22px; }
.kicker { color:var(--teal); font:700 12px/1.2 ui-monospace, SFMono-Regular, Consolas, monospace; letter-spacing:1.5px; text-transform:uppercase; }
h1 { margin:7px 0 5px; font-size:clamp(30px,4vw,52px); line-height:.98; letter-spacing:0; }
.subtitle { margin:0; color:var(--muted); font-size:16px; }
.badges { display:flex; flex-wrap:wrap; gap:8px; justify-content:flex-end; }
.badge { border:1px solid var(--line); background:rgba(255,255,255,.7); border-radius:5px; padding:8px 10px; color:var(--muted); font:12px ui-monospace, SFMono-Regular, Consolas, monospace; }
.badge strong { color:var(--navy); }
.layout { display:grid; grid-template-columns:minmax(0,1fr) 310px; gap:18px; align-items:start; }
.panel { background:rgba(255,255,255,.9); border:1px solid var(--line); border-radius:8px; box-shadow:0 12px 32px rgba(28,48,61,.07); }
.chat { min-height:650px; display:flex; flex-direction:column; overflow:hidden; }
.messages { flex:1; padding:22px; overflow:auto; }
.empty { display:grid; place-items:center; min-height:480px; color:var(--muted); text-align:center; }
.empty h2 { color:var(--navy); font-size:26px; margin:0 0 8px; }
.message { display:flex; margin:0 0 18px; gap:10px; }
.message.user { justify-content:flex-end; }
.bubble { max-width:min(760px,88%); padding:13px 15px; border:1px solid var(--line); border-radius:8px; background:#fff; white-space:pre-wrap; line-height:1.45; }
.user .bubble { background:var(--navy); border-color:var(--navy); color:#fff; }
.label { color:var(--muted); font:11px ui-monospace, SFMono-Regular, Consolas, monospace; margin:0 0 5px; text-transform:uppercase; }
.user .label { text-align:right; }
.tool { margin:8px 0 0 22px; border-left:3px solid var(--teal); padding:10px 12px; background:#f2f8f7; border-radius:0 6px 6px 0; font-size:14px; }
.tool.error { border-left-color:var(--red); background:#fff5f4; }
.tool-head { display:flex; justify-content:space-between; gap:12px; color:var(--teal); font:700 12px ui-monospace, SFMono-Regular, Consolas, monospace; }
.tool.error .tool-head { color:var(--red); }
details { margin-top:7px; } summary { color:var(--muted); cursor:pointer; font:12px ui-monospace, SFMono-Regular, Consolas, monospace; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; margin:7px 0 0; color:#33414d; font:12px/1.4 ui-monospace, SFMono-Regular, Consolas, monospace; }
.composer { border-top:1px solid var(--line); padding:15px; background:#fbfcfc; }
textarea { width:100%; min-height:76px; resize:vertical; border:1px solid #cbd5da; border-radius:6px; padding:12px; color:var(--ink); background:#fff; outline:none; }
textarea:focus { border-color:var(--teal); box-shadow:0 0 0 3px rgba(8,127,120,.12); }
.actions { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-top:10px; }
.hint { color:var(--muted); font:12px ui-monospace, SFMono-Regular, Consolas, monospace; }
.primary, .secondary { border-radius:5px; padding:9px 14px; border:1px solid; }
.primary { color:#fff; background:var(--teal); border-color:var(--teal); }
.primary:disabled { opacity:.55; cursor:wait; }
.secondary { color:var(--navy); background:#fff; border-color:#c8d2d8; }
.side { padding:18px; }
.side h2 { margin:0 0 15px; color:var(--navy); font-size:21px; }
.meta { display:grid; gap:10px; margin-bottom:20px; }
.meta-row { border-bottom:1px solid var(--line); padding-bottom:9px; }
.meta-label { display:block; color:var(--muted); font:11px ui-monospace, SFMono-Regular, Consolas, monospace; text-transform:uppercase; margin-bottom:4px; }
.meta-value { overflow-wrap:anywhere; font-size:14px; }
.side-note { color:var(--muted); font-size:14px; line-height:1.5; border-top:1px solid var(--line); padding-top:15px; }
.transcript-actions { display:flex; gap:8px; margin-top:8px; }
.transcript-actions button { flex:1; padding:7px 8px; font-size:12px; }
.trace-error { margin:10px 0; padding:10px 12px; color:#8f2f2f; background:#fff0ef; border:1px solid #e6b7b3; border-radius:6px; font:12px/1.4 ui-monospace, SFMono-Regular, Consolas, monospace; white-space:pre-wrap; }
.status { color:var(--teal); }
@media (max-width:820px) { .shell { padding:20px 12px; } .topbar { display:block; } .badges { justify-content:flex-start; margin-top:15px; } .layout { grid-template-columns:1fr; } .side { order:-1; } .chat { min-height:620px; } }
</style>
</head>
<body>
<main class="shell">
<header class="topbar">
<div><div class="kicker">Northstar Labs / Internal Service Desk</div><h1>Helpdesk Console</h1><p class="subtitle">Một phiên chat, một trace rõ ràng, không che khuất tool.</p></div>
<div class="badges"><span class="badge">VERSION <strong id="version">...</strong></span><span class="badge">MODEL <strong id="model">...</strong></span><span class="badge" id="state">READY</span></div>
</header>
<section class="layout">
<div class="panel chat"><div class="messages" id="messages"><div class="empty"><div><h2>Chưa có lượt chat</h2><p>Hỏi về VPN, email, Wi-Fi, thiết bị hoặc policy nội bộ.</p></div></div></div>
<form class="composer" id="composer"><textarea id="input" placeholder="Ví dụ: Kiểm tra riêng VPN trên LT-204..." required></textarea><div class="actions"><span class="hint">Ctrl/⌘ + Enter để gửi</span><div><button class="secondary" id="clear" type="button">Xóa phiên</button> <button class="primary" id="send" type="submit">Gửi yêu cầu</button></div></div></form></div>
<aside class="panel side"><h2>Session trace</h2><div class="meta"><div class="meta-row"><span class="meta-label">Transcript</span><span class="meta-value" id="transcript">Chưa có lượt nào</span><div class="transcript-actions"><button class="secondary" id="open-transcript" type="button" disabled>Mở JSON</button><button class="secondary" id="download-transcript" type="button" disabled>Tải xuống</button></div></div><div class="meta-row"><span class="meta-label">Provider</span><span class="meta-value" id="provider">...</span></div><div class="meta-row"><span class="meta-label">Tool events</span><span class="meta-value" id="events">0</span></div><div class="meta-row"><span class="meta-label">Last status</span><span class="meta-value status" id="last-status">ready</span></div></div><p class="side-note">Mỗi lượt lưu user input, assistant response, tool name, arguments, kết quả hoặc lỗi. Transcript dùng trực tiếp làm evidence cho demo.</p></aside>
</section></main>
<script>
const $ = (id) => document.getElementById(id);
let sessionId = crypto.randomUUID();
let eventCount = 0;
let transcriptPath = '';
function esc(value) { const div = document.createElement('div'); div.textContent = value ?? ''; return div.innerHTML; }
function pretty(value) { return JSON.stringify(value ?? {}, null, 2); }
function normalizeText(value) { return String(value ?? '').normalize('NFC'); }
function setTranscript(path) { transcriptPath = path || ''; $('transcript').textContent = transcriptPath ? transcriptPath.split(/[\\/]/).pop() : 'Chưa có lượt nào'; $('open-transcript').disabled = !transcriptPath; $('download-transcript').disabled = !transcriptPath; }
function showTraceError(message) { const root = $('messages'); const item = document.createElement('div'); item.className = 'trace-error'; item.textContent = normalizeText(message); root.appendChild(item); root.scrollTop = root.scrollHeight; }
function addMessage(role, text, tools=[]) {
  const root = $('messages'); const empty = root.querySelector('.empty'); if (empty) empty.remove();
  const item = document.createElement('article'); item.className = `message ${role}`;
  let body = `<div><div class="label">${role === 'user' ? 'You' : 'Agent'}</div><div class="bubble">${esc(text || '')}</div>`;
  tools.forEach((event) => {
    const result = event.result || {}; const error = result.error || result.status === 'error';
    body += `<div class="tool ${error ? 'error' : ''}"><div class="tool-head"><span>${error ? 'TOOL ERROR' : 'TOOL'} / ${esc(event.tool)}</span><span>${error ? esc(result.error || 'error') : 'RESULT'}</span></div><details><summary>input</summary><pre>${esc(pretty(event.args))}</pre></details><details open><summary>${error ? 'error detail' : 'result detail'}</summary><pre>${esc(pretty(result))}</pre></details></div>`;
    eventCount += 1;
  });
  item.innerHTML = body + '</div>'; root.appendChild(item); root.scrollTop = root.scrollHeight; $('events').textContent = eventCount;
}
async function init() { const response = await fetch('/api/info'); const data = await response.json(); $('version').textContent = data.artifact_version; $('model').textContent = data.model; $('provider').textContent = data.provider; }
async function streamChat(text) {
    const response = await fetch('/api/chat/stream', {method:'POST', headers:{'Content-Type':'application/json; charset=utf-8', 'Accept':'text/event-stream'}, body:JSON.stringify({session_id:sessionId, text:normalizeText(text)})});
    if (!response.ok || !response.body) { const data = await response.json().catch(() => ({})); throw new Error(data.error || 'Request failed'); }
    const reader = response.body.getReader(); const decoder = new TextDecoder('utf-8'); let buffer = ''; let assistant = ''; let assistantItem = null; const tools = [];
    const renderAssistant = () => { if (!assistantItem) { const root = $('messages'); const empty = root.querySelector('.empty'); if (empty) empty.remove(); assistantItem = document.createElement('article'); assistantItem.className = 'message assistant'; assistantItem.innerHTML = '<div><div class="label">Agent</div><div class="bubble"></div><div class="stream-tools"></div></div>'; root.appendChild(assistantItem); } assistantItem.querySelector('.bubble').textContent = assistant; $('messages').scrollTop = $('messages').scrollHeight; };
    const handle = (line) => { if (!line.startsWith('data:')) return; const event = JSON.parse(line.slice(5).trim()); if (event.type === 'token') { assistant += normalizeText(event.text); renderAssistant(); } else if (event.type === 'tool') { tools.push(event.event); eventCount += 1; $('events').textContent = eventCount; } else if (event.type === 'done') { if (!assistant) { assistant = normalizeText(event.assistant_text); renderAssistant(); } if (tools.length) { assistantItem.querySelector('.stream-tools').innerHTML = tools.map((tool) => { const result = tool.result || {}; const error = result.error || result.status === 'error'; return `<div class="tool ${error ? 'error' : ''}"><div class="tool-head"><span>${error ? 'TOOL ERROR' : 'TOOL'} / ${esc(tool.tool)}</span><span>${error ? esc(result.error || 'error') : 'RESULT'}</span></div><details><summary>input</summary><pre>${esc(pretty(tool.args))}</pre></details><details open><summary>${error ? 'error detail' : 'result detail'}</summary><pre>${esc(pretty(result))}</pre></details></div>`; }).join(''); } setTranscript(event.transcript_path); if (event.error) showTraceError(event.error); $('last-status').textContent = event.status || 'answered'; } else if (event.type === 'error') { throw new Error(event.message || 'Streaming request failed'); } };
    while (true) { const {value, done} = await reader.read(); buffer += decoder.decode(value || new Uint8Array(), {stream: !done}); const records = buffer.split('\n\n'); buffer = records.pop() || ''; records.forEach((record) => record.split('\n').forEach(handle)); if (done) break; }
}
$('composer').addEventListener('submit', async (event) => { event.preventDefault(); const input = $('input'); const text = normalizeText(input.value).trim(); if (!text) return; addMessage('user', text); input.value=''; $('send').disabled=true; $('state').textContent='RUNNING'; $('last-status').textContent='running';
    try { await streamChat(text); $('state').textContent='READY'; } catch (error) { addMessage('assistant', `Không thể hoàn thành yêu cầu: ${error.message}`); showTraceError(error.message); $('state').textContent='ERROR'; $('last-status').textContent='provider_error'; } finally { $('send').disabled=false; input.focus(); }
});
 $('clear').addEventListener('click', () => { sessionId=crypto.randomUUID(); eventCount=0; setTranscript(''); $('events').textContent='0'; $('last-status').textContent='ready'; $('state').textContent='READY'; $('messages').innerHTML='<div class="empty"><div><h2>Chưa có lượt chat</h2><p>Hỏi về VPN, email, Wi-Fi, thiết bị hoặc policy nội bộ.</p></div></div>'; });
 $('open-transcript').addEventListener('click', () => { if (transcriptPath) window.open(`/api/transcript?session_id=${encodeURIComponent(sessionId)}`, '_blank', 'noopener'); });
 $('download-transcript').addEventListener('click', () => { if (transcriptPath) window.location.href = `/api/transcript?session_id=${encodeURIComponent(sessionId)}&download=1`; });
$('input').addEventListener('keydown', (event) => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') $('composer').requestSubmit(); });
init().catch(() => { $('state').textContent='CONFIG ERROR'; });
</script>
</body></html>"""


class AppState:
    def __init__(self, provider: Any, tools: list[dict[str, Any]], model: str | None, version: dict[str, str], transcripts_dir: Path, max_tool_rounds: int) -> None:
        self.provider = provider
        self.tools = tools
        self.model = model
        self.version = version
        self.transcripts_dir = transcripts_dir
        self.max_tool_rounds = max_tool_rounds
        self.sessions: dict[str, dict[str, Any]] = {}
        self.lock = threading.Lock()

    def session(self, session_id: str) -> dict[str, Any]:
        with self.lock:
            if session_id not in self.sessions:
                transcript_id = f"web_{safe_slug(self.version['version'])}_{uuid.uuid4().hex[:12]}"
                self.sessions[session_id] = {
                    "transcript_id": transcript_id,
                    **self.version,
                    "provider": self.provider_name,
                    "model": self.model,
                    "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
                    "tools": str(ARTIFACTS_DIR / "tools.yaml"),
                    "history_window": 5,
                    "max_tool_rounds": self.max_tool_rounds,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "turns": [],
                    "history": [],
                }
            return self.sessions[session_id]

    @property
    def provider_name(self) -> str:
        return getattr(self.provider, "name", None) or self.provider.__class__.__name__


class Handler(BaseHTTPRequestHandler):
    state: AppState

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_sse(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str)
        self.wfile.write(f"data: {body}\n\n".encode("utf-8"))
        self.wfile.flush()

    def send_transcript(self, session_id: str, download: bool = False) -> None:
        session = self.state.session(session_id)
        payload = {key: value for key, value in session.items() if key != "history"}
        body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{session["transcript_id"]}.transcript.json"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/info":
            self.send_json({"artifact_version": self.state.version["artifact_version"], "model": self.state.model, "provider": self.state.provider_name})
        elif path == "/api/transcript":
            query = dict(item.split("=", 1) for item in urlparse(self.path).query.split("&") if "=" in item)
            session_id = query.get("session_id", "")
            if not session_id or session_id not in self.state.sessions:
                self.send_json({"error": "session_not_found"}, 404)
                return
            self.send_transcript(session_id, query.get("download") == "1")
        else:
            self.send_json({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        path_name = urlparse(self.path).path
        if path_name not in {"/api/chat", "/api/chat/stream"}:
            self.send_json({"error": "not_found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            text = unicodedata.normalize("NFC", str(payload.get("text", ""))).strip()
            session_id = unicodedata.normalize("NFC", str(payload.get("session_id", ""))).strip()
            if not text or not session_id:
                self.send_json({"error": "text and session_id are required"}, 400)
                return
            streaming = path_name == "/api/chat/stream"
            if streaming:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache, no-transform")
                self.send_header("Connection", "keep-alive")
                self.send_header("X-Accel-Buffering", "no")
                self.end_headers()
                self.send_sse({"type": "status", "status": "running"})
            session = self.state.session(session_id)
            turn_index = len(session["turns"]) + 1
            messages = [{"role": "system", "content": self.server.system_prompt}, *session["history"][-10:], {"role": "user", "content": text}]
            turn: dict[str, Any] = {"turn_index": turn_index, "started_at": now_iso(), "user": text, "status": "started", "assistant_text": None, "rounds": [], "tool_events": []}
            try:
                result = run_model_tool_loop(provider=self.state.provider, messages=messages, tools=self.state.tools, model=self.state.model, max_tool_rounds=self.state.max_tool_rounds)
                turn.update(result)
                assistant_text = result["assistant_text"]
                session["history"].extend([{"role": "user", "content": text}, {"role": "assistant", "content": assistant_text}])
            except Exception as exc:
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
                assistant_text = "Không thể kết nối provider. Xem lỗi trong transcript."
            turn["ended_at"] = now_iso()
            session["turns"].append(turn)
            path = self.state.transcripts_dir / f"{session['transcript_id']}.transcript.json"
            write_transcript(path, {key: value for key, value in session.items() if key != "history"})
            if streaming:
                for event in turn.get("tool_events", []):
                    self.send_sse({"type": "tool", "event": event})
                for index in range(0, len(assistant_text), 24):
                    self.send_sse({"type": "token", "text": assistant_text[index:index + 24]})
                    time.sleep(0.012)
                self.send_sse({"type": "done", "status": turn.get("status"), "assistant_text": assistant_text, "tool_events": turn.get("tool_events", []), "transcript_path": str(path), "turn_index": turn_index})
                return
            self.send_json({"status": turn.get("status"), "assistant_text": assistant_text, "tool_events": turn.get("tool_events", []), "transcript_path": str(path), "turn_index": turn_index})
        except Exception as exc:
            if "streaming" in locals() and streaming:
                try:
                    self.send_sse({"type": "error", "message": f"{type(exc).__name__}: {exc}"})
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                self.send_json({"error": f"{type(exc).__name__}: {exc}"}, 500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Web UI for the Northstar IT Helpdesk Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    state = AppState(provider, to_openai_tools(load_tool_declarations(tools_path)), model, artifact_version_dict(build_artifact_version(args.version, prompt_path, tools_path)), args.transcripts_dir, args.max_tool_rounds)
    Handler.state = state
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.system_prompt = prompt_path.read_text(encoding="utf-8")
    print(f"Northstar Helpdesk UI: http://{args.host}:{args.port}")
    print(f"artifact_version={state.version['artifact_version']}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
