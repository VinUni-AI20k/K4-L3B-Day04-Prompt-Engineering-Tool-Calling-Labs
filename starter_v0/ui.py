from __future__ import annotations

import argparse
import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

load_lab_env(ROOT)


HTML = r'''<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nova Laptop | Agent Console</title>
  <style>
    :root { --ink:#17222d; --muted:#687684; --line:#dce5e8; --panel:#fff; --accent:#e56b45; --accent-dark:#a6422d; --teal:#146c70; --teal-soft:#e8f4f0; --ok:#287b5a; --bad:#b64242; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:radial-gradient(circle at 8% 0%,#fff7ed 0 18%,transparent 42%),linear-gradient(135deg,#f3f7f4 0%,#fff 55%,#edf5f4 100%); font:15px/1.5 'Segoe UI', Arial, sans-serif; min-height:100vh; }
    .shell { width:min(1420px, calc(100% - 40px)); margin:0 auto; padding:32px 0 42px; }
    header { display:flex; justify-content:space-between; align-items:center; gap:28px; border-bottom:1px solid var(--line); padding-bottom:24px; }
    .eyebrow { color:var(--accent-dark); font:700 clamp(22px,3vw,32px)/1.1 'Segoe UI', Arial, sans-serif; letter-spacing:.1px; }
    .version { border:1px solid #efb19d; background:rgba(255,244,238,.86); padding:15px 17px; min-width:275px; box-shadow:8px 8px 0 rgba(229,107,69,.09); }
    .version strong { display:flex; align-items:center; gap:8px; color:var(--accent-dark); font:700 12px 'Segoe UI', Arial, sans-serif; letter-spacing:.5px; text-transform:uppercase; }
    .version strong::before { content:''; width:8px; height:8px; border-radius:50%; background:#45a66f; box-shadow:0 0 0 4px rgba(69,166,111,.14); }
    .version code { display:block; margin-top:5px; overflow-wrap:anywhere; color:#713b2c; font:12px Consolas,monospace; }
    .layout { display:grid; grid-template-columns:minmax(0,1.08fr) minmax(360px,.92fr); gap:22px; margin-top:26px; }
    .panel { background:rgba(255,255,255,.8); border:1px solid rgba(185,205,205,.72); box-shadow:0 18px 45px rgba(41,65,67,.09); backdrop-filter:blur(10px); }
    .chat-panel { display:flex; flex-direction:column; min-height:650px; border-top:4px solid var(--accent); }
    .trace-panel { min-height:650px; overflow:auto; border-top:4px solid var(--teal); }
    .panel-head { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:16px 20px; border-bottom:1px solid var(--line); font:700 13px 'Segoe UI', Arial, sans-serif; letter-spacing:.2px; }
    .panel-head span { color:var(--muted); font-weight:400; }
    #messages { flex:1; overflow:auto; padding:24px; }
    .message { max-width:88%; margin:0 0 17px; animation:rise .25s ease-out; }
    .message.user { margin-left:auto; }
    .message .label { color:var(--muted); font:700 11px 'Segoe UI', Arial, sans-serif; letter-spacing:.8px; text-transform:uppercase; margin-bottom:5px; }
    .bubble { padding:14px 16px; white-space:pre-wrap; border:1px solid var(--line); background:#fff; box-shadow:0 5px 14px rgba(41,65,67,.04); }
    .user .bubble { background:#fff0e9; border-color:#f2c7b8; }
    .assistant .bubble { background:#edf7f4; border-color:#c8e2d8; }
    .empty { color:var(--muted); opacity:.62; text-align:center; padding:100px 25px; font:400 14px/1.5 'Segoe UI', Arial, sans-serif; }
    form { border-top:1px solid var(--line); padding:18px; display:flex; gap:10px; background:rgba(248,251,249,.8); }
    textarea { resize:vertical; min-height:56px; max-height:160px; flex:1; border:1px solid #bfcfd1; padding:13px 14px; color:var(--ink); background:#fff; font:15px 'Segoe UI', Arial, sans-serif; outline:none; }
    textarea:focus { border-color:var(--teal); box-shadow:0 0 0 3px rgba(20,108,112,.1); }
    button { border:0; background:var(--accent); color:#fff; min-width:72px; padding:0 18px; cursor:pointer; font:700 13px 'Segoe UI', Arial, sans-serif; box-shadow:4px 4px 0 rgba(166,66,45,.18); }
    button:hover { background:var(--accent-dark); } button:disabled { opacity:.55; cursor:wait; }
    #trace { padding:18px 20px; }
    .trace-turn { border-left:3px solid var(--teal); margin:0 0 18px; padding-left:14px; }
    .trace-title { display:flex; justify-content:space-between; color:var(--teal); font:700 12px 'Segoe UI', Arial, sans-serif; }
    .trace-status { color:var(--ok); } .trace-status.bad { color:var(--bad); }
    details { margin-top:10px; border:1px solid var(--line); background:#fbfcfc; }
    summary { cursor:pointer; padding:9px 11px; font:700 12px 'Segoe UI', Arial, sans-serif; }
    pre { margin:0; padding:11px; border-top:1px solid var(--line); overflow:auto; white-space:pre-wrap; word-break:break-word; background:#17222d; color:#dce9e5; font:12px/1.45 Consolas,monospace; }
    .trace-hint { display:none; }
    @keyframes rise { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:none; } }
    @media (max-width: 860px) { .shell{width:min(100% - 20px,680px);padding-top:18px} header{display:block}.version{margin-top:18px}.layout{grid-template-columns:1fr}.chat-panel,.trace-panel{min-height:520px} }
  </style>
</head>
<body>
  <main class="shell">
    <header>
    <div><div class="eyebrow">Nova Laptop Agent</div></div>
      <div class="version"><strong>Đang chạy</strong><code id="artifact">loading...</code><span id="provider"></span></div>
    </header>
    <section class="layout">
    <div class="panel chat-panel"><div class="panel-head">Conversation <span id="turn-count">0 turns</span></div><div id="messages"><div class="empty">Nhập yêu cầu để bắt đầu cuộc trò chuyện</div></div><form id="composer"><textarea id="prompt" placeholder="Lọc laptop Acer dùng thiết kế, tối đa 26 triệu..." required></textarea><button id="send" type="submit">Gửi</button></form></div>
    <aside class="panel trace-panel"><div class="panel-head">Execution trace <span>live</span></div><div class="trace-hint"></div><div id="trace"><div class="empty">Thông tin tool sẽ xuất hiện ở đây</div></div></aside>
    </section>
  </main>
<script>
const messages = document.querySelector('#messages'), trace = document.querySelector('#trace'), promptBox = document.querySelector('#prompt'), send = document.querySelector('#send');
const pretty = value => JSON.stringify(value, null, 2);
function displayReply(text) { if (!text) return ''; try { const candidate=text.trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,''); const payload=JSON.parse(candidate); return typeof payload.reply==='string' && payload.reply.trim() ? payload.reply.trim() : text; } catch(error) { return text; } }
function addMessage(kind, text) { const wrap=document.createElement('div'); wrap.className='message '+kind; wrap.innerHTML='<div class="label">'+(kind==='user'?'You':'Agent')+'</div><div class="bubble"></div>'; wrap.querySelector('.bubble').textContent=text||'(no text)'; const empty=messages.querySelector('.empty'); if(empty) empty.remove(); messages.appendChild(wrap); messages.scrollTop=messages.scrollHeight; }
function addTrace(turn) { const empty=trace.querySelector('.empty'); if(empty) empty.remove(); const box=document.createElement('section'); box.className='trace-turn'; const status=turn.status==='provider_error'?'bad':''; let html='<div class="trace-title"><span>TURN '+turn.turn_index+' · '+turn.status+'</span><span class="trace-status '+status+'">'+(turn.status==='answered'?'observed':'inspect')+'</span></div>'; if(turn.error) html+='<details open><summary>ERROR</summary><pre></pre></details>'; (turn.tool_events||[]).forEach((event,index)=>{ html+='<details open><summary>TOOL '+(index+1)+' · '+event.tool+'</summary><pre></pre><pre></pre></details>'; }); box.innerHTML=html; const pres=box.querySelectorAll('pre'); let i=0; if(turn.error) pres[i++].textContent=turn.error; (turn.tool_events||[]).forEach(event=>{pres[i++].textContent='INPUT\n'+pretty(event.args||{}); pres[i++].textContent='RESULT\n'+pretty(event.result);}); trace.prepend(box); }
async function load() { const r=await fetch('/api/state'); const data=await r.json(); document.querySelector('#artifact').textContent=data.artifact_version; document.querySelector('#provider').textContent=data.provider+' / '+(data.model||'default'); }
document.querySelector('#composer').addEventListener('submit', async event => { event.preventDefault(); const text=promptBox.value.trim(); if(!text)return; addMessage('user',text); promptBox.value=''; send.disabled=true; send.textContent='...'; try { const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})}); const data=await r.json(); if(!r.ok) throw new Error(data.error||'Request failed'); addMessage('assistant',displayReply(data.turn.assistant_text||data.turn.error)); addTrace(data.turn); document.querySelector('#turn-count').textContent=data.turn_count+' turns'; } catch(error) { addMessage('assistant','UI error: '+error.message); } finally { send.disabled=false; send.textContent='Gửi'; promptBox.focus(); } });
load();
</script>
</body></html>'''


class ChatSession:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.system_prompt = args.system_prompt.read_text(encoding="utf-8")
        self.tool_declarations = load_tool_declarations(args.tools)
        self.openai_tools = to_openai_tools(self.tool_declarations)
        self.provider = make_provider(args.provider)
        self.selected_model = args.model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        self.transcript_id = "_".join([safe_slug(args.version), safe_slug(args.provider), "ui", timestamp])
        self.transcript_path = args.transcripts_dir / f"{self.transcript_id}.transcript.json"
        self.history: list[dict[str, str]] = []
        self.lock = threading.Lock()
        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": args.provider,
            "model": self.selected_model,
            "system_prompt": str(args.system_prompt),
            "tools": str(args.tools),
            "history_window": args.history_window,
            "max_tool_rounds": args.max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "ui": True,
            "turns": [],
        }
        write_transcript(self.transcript_path, self.transcript)

    def state(self) -> dict[str, Any]:
        return {**artifact_version_dict(self.artifact_version), "provider": self.args.provider, "model": self.selected_model, "transcript": str(self.transcript_path), "turn_count": len(self.transcript["turns"])}

    def chat(self, user_text: str) -> dict[str, Any]:
        with self.lock:
            turn_index = len(self.transcript["turns"]) + 1
            messages = [{"role": "system", "content": self.system_prompt}, *trim_history(self.history, self.args.history_window), {"role": "user", "content": user_text}]
            turn: dict[str, Any] = {"turn_index": turn_index, "started_at": now_iso(), "user": user_text, "status": "started", "assistant_text": None, "rounds": [], "tool_events": []}
            try:
                result = run_model_tool_loop(provider=self.provider, messages=messages, tools=self.openai_tools, model=self.args.model, max_tool_rounds=self.args.max_tool_rounds)
                turn.update(result)
                self.history.extend([{"role": "user", "content": user_text}, {"role": "assistant", "content": result["assistant_text"]}])
            except Exception as exc:
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {str(exc)}"})
            turn["ended_at"] = now_iso()
            self.transcript["turns"].append(turn)
            write_transcript(self.transcript_path, self.transcript)
            return turn


class Handler(BaseHTTPRequestHandler):
    session: ChatSession

    def _send(self, payload: Any, status: int = 200, content_type: str = "application/json") -> None:
        data = payload if isinstance(payload, bytes) else (json.dumps(payload, ensure_ascii=False).encode("utf-8") if content_type == "application/json" else payload.encode("utf-8"))
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/": self._send(HTML, content_type="text/html")
        elif path == "/api/state": self._send(self.session.state())
        else: self._send({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat": self._send({"error": "not_found"}, 404); return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length))
            message = str(body.get("message", "")).strip()
            if not message: raise ValueError("message is required")
            turn = self.session.chat(message)
            self._send({"turn": turn, "turn_count": len(self.session.transcript["turns"]), "transcript": str(self.session.transcript_path)})
        except Exception as exc:
            self._send({"error": f"{type(exc).__name__}: {str(exc)}"}, 400)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Nova Laptop web chat using the team's conversation handler.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()
    session = ChatSession(args)
    Handler.session = session
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Nova Laptop UI: http://{args.host}:{args.port}/")
    print(f"artifact_version={session.artifact_version.artifact_version}")
    print(f"transcript={session.transcript_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
