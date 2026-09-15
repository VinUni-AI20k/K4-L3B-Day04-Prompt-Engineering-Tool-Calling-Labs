"""Dependency-free web UI for the Day04 Helpdesk agent.

This entry point deliberately reuses the same prompt, tool declarations and
agent loop as ``chat.py``. It adds only a browser interface and transcript
display for the required lab demo.
"""

from __future__ import annotations

import argparse
import json
import threading
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>Northstar Service Desk</title>
  <style>
    :root {
      --blue: #2563eb;
      --blue-dark: #1d4ed8;
      --green: #047857;
      --ink: #0f172a;
      --muted-ink: #475569;
      --muted: #f1f5fd;
      --surface: #ffffff;
      --border: #dbe5f4;
      --danger: #b91c1c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-width: 320px;
      background: #f7faff;
      color: var(--ink);
      font-family: "Fira Sans", ui-sans-serif, system-ui, sans-serif;
      font-size: 16px;
      line-height: 1.5;
    }
    button, textarea { font: inherit; }
    button { cursor: pointer; }
    button:focus-visible, textarea:focus-visible { outline: 3px solid rgba(37, 99, 235, .35); outline-offset: 2px; }
    .shell { display: grid; grid-template-columns: 270px minmax(0, 1fr); min-height: 100vh; max-width: 1440px; margin: 0 auto; }
    .sidebar { display: flex; flex-direction: column; gap: 26px; padding: 28px 22px; background: var(--ink); color: #cbd5e1; }
    .brand { display: flex; align-items: center; gap: 10px; color: #fff; font-size: 12px; font-weight: 700; letter-spacing: .1em; }
    .brand-mark { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid #60a5fa; border-radius: 10px; color: #bfdbfe; font-family: "Fira Code", monospace; font-size: 11px; }
    .sidebar h1 { margin: 0; color: #fff; font-size: 23px; line-height: 1.15; letter-spacing: -.02em; }
    .sidebar p { margin: 0; color: #94a3b8; font-size: 14px; }
    .side-block { padding-top: 20px; border-top: 1px solid #293548; }
    .side-label { margin: 0 0 8px; color: #94a3b8; font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .capabilities { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
    .capabilities li { display: flex; gap: 8px; font-size: 14px; }
    .capabilities li::before { content: ""; flex: 0 0 6px; height: 6px; margin-top: 8px; border-radius: 99px; background: #34d399; }
    .footer-note { margin-top: auto; color: #64748b; font-family: "Fira Code", monospace; font-size: 11px; }
    .main { display: flex; flex-direction: column; min-width: 0; }
    .topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 20px clamp(20px, 4vw, 52px); border-bottom: 1px solid var(--border); background: rgba(255,255,255,.92); }
    .eyebrow { margin: 0 0 2px; color: var(--muted-ink); font-size: 13px; }
    .topbar h2 { margin: 0; font-size: 21px; line-height: 1.2; letter-spacing: -.02em; }
    .version { display: inline-flex; align-items: center; min-height: 34px; padding: 5px 9px; border: 1px solid #bfdbfe; border-radius: 8px; background: #eff6ff; color: #1e40af; font-family: "Fira Code", monospace; font-size: 11px; white-space: nowrap; }
    .content { display: flex; flex: 1; flex-direction: column; width: min(100%, 980px); margin: 0 auto; padding: 30px clamp(20px, 4vw, 52px) 26px; }
    .intro { margin-bottom: 20px; }
    .intro h3 { margin: 0 0 5px; font-size: 27px; letter-spacing: -.035em; }
    .intro p { max-width: 700px; margin: 0; color: var(--muted-ink); }
    .messages { display: flex; flex: 1; flex-direction: column; gap: 15px; min-height: 300px; padding: 4px 2px 23px; }
    .empty { display: grid; flex: 1; min-height: 250px; place-items: center; padding: 28px; border: 1px dashed #bfd0e8; border-radius: 14px; color: var(--muted-ink); text-align: center; }
    .empty strong { display: block; margin-bottom: 4px; color: var(--ink); }
    .message { display: flex; gap: 10px; max-width: 86%; animation: rise .2s ease-out; }
    .message.user { align-self: flex-end; flex-direction: row-reverse; }
    .avatar { display: grid; flex: 0 0 34px; width: 34px; height: 34px; place-items: center; border-radius: 10px; background: #dbeafe; color: #1e40af; font-family: "Fira Code", monospace; font-size: 10px; font-weight: 600; }
    .user .avatar { background: #d1fae5; color: #047857; }
    .bubble { padding: 11px 14px; border: 1px solid var(--border); border-radius: 13px; background: var(--surface); box-shadow: 0 5px 18px rgba(15, 23, 42, .04); white-space: pre-wrap; overflow-wrap: anywhere; }
    .user .bubble { border-color: #bfdbfe; background: #eff6ff; }
    .meta { margin-top: 4px; color: #64748b; font-size: 11px; }
    .trace { align-self: stretch; margin-left: 44px; padding: 13px; border: 1px solid #cbd5e1; border-left: 3px solid var(--green); border-radius: 10px; background: #f8fafc; }
    .trace-title { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 8px; color: #065f46; font-size: 13px; font-weight: 700; }
    .tool { margin-top: 8px; border: 1px solid var(--border); border-radius: 8px; background: #fff; overflow: hidden; }
    .tool summary { cursor: pointer; padding: 8px 10px; color: #1e3a8a; font-family: "Fira Code", monospace; font-size: 12px; font-weight: 600; }
    .tool pre { margin: 0; padding: 9px 10px; border-top: 1px solid #e2e8f0; color: #334155; font-family: "Fira Code", monospace; font-size: 11px; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }
    .tool pre.error { color: var(--danger); background: #fff7f7; }
    .composer { padding-top: 15px; border-top: 1px solid var(--border); }
    .composer label { display: block; margin-bottom: 7px; color: var(--muted-ink); font-size: 13px; font-weight: 600; }
    .composer-row { display: flex; align-items: flex-end; gap: 10px; }
    textarea { flex: 1; min-height: 50px; max-height: 170px; resize: vertical; padding: 12px 13px; border: 1px solid #b9c9df; border-radius: 10px; background: #fff; color: var(--ink); line-height: 1.45; }
    textarea::placeholder { color: #64748b; }
    .button { min-height: 46px; padding: 10px 16px; border: 1px solid transparent; border-radius: 9px; font-weight: 600; transition: background-color .2s ease, border-color .2s ease, transform .2s ease; }
    .button:active { transform: translateY(1px); }
    .primary { background: var(--blue); color: #fff; }
    .primary:hover { background: var(--blue-dark); }
    .primary:disabled { cursor: wait; opacity: .65; }
    .quiet { margin-top: 9px; padding: 3px 0; border: 0; background: transparent; color: var(--muted-ink); font-size: 13px; }
    .quiet:hover { color: var(--blue-dark); text-decoration: underline; }
    .status { min-height: 22px; margin-top: 7px; color: var(--muted-ink); font-size: 12px; }
    .status.error { color: var(--danger); }
    @keyframes rise { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
    @media (max-width: 820px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { gap: 12px; padding: 16px 20px; }
      .sidebar h1 { font-size: 20px; }
      .side-block, .footer-note { display: none; }
      .topbar { padding: 17px 20px; }
      .content { padding: 23px 20px; }
      .message { max-width: 96%; }
      .trace { margin-left: 0; }
    }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; } }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar" aria-label="Service desk information">
      <div class="brand"><span class="brand-mark" aria-hidden="true">NS</span><span>NORTHSTAR LABS</span></div>
      <div><h1>Service desk</h1><p>Evidence-first support for internal IT requests.</p></div>
      <div class="side-block"><p class="side-label">Available actions</p><ul class="capabilities"><li>Search internal knowledge</li><li>Check service status</li><li>Inspect registered devices</li><li>Create tickets after confirmation</li></ul></div>
      <div class="footer-note">FICTIONAL DATA / LOCAL DEMO</div>
    </aside>
    <main class="main">
      <header class="topbar"><div><p class="eyebrow">Internal support workspace</p><h2>Ask the service desk</h2></div><code id="version" class="version" aria-label="Artifact version">loading version</code></header>
      <div class="content">
        <section class="intro" aria-labelledby="intro-title"><h3 id="intro-title">What can we help with?</h3><p>Describe an IT issue or request. The trace below shows the selected tool and its returned evidence.</p></section>
        <section id="messages" class="messages" aria-label="Conversation" aria-live="polite" role="log"><div id="empty" class="empty"><div><strong>Start a support conversation</strong><span>Try VPN, email, Wi-Fi, a device, or a knowledge article.</span></div></div></section>
        <form id="composer" class="composer"><label for="input">Describe your request</label><div class="composer-row"><textarea id="input" rows="2" maxlength="6000" placeholder="Example: Is VPN production currently experiencing an incident?" required></textarea><button id="send" class="button primary" type="submit">Send</button></div><button id="clear" class="quiet" type="button">Start a new conversation</button><div id="status" class="status" role="status" aria-live="polite"></div></form>
      </div>
    </main>
  </div>
  <script>
    const config = __APP_CONFIG__;
    const messages = document.getElementById('messages');
    const empty = document.getElementById('empty');
    const input = document.getElementById('input');
    const send = document.getElementById('send');
    const status = document.getElementById('status');
    document.getElementById('version').textContent = config.artifact_version;
    let sessionId = newSessionId();
    function newSessionId() { return (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : 'ui-' + Date.now() + '-' + Math.random().toString(16).slice(2); }
    function escapeHtml(value) { return String(value ?? '').replace(/[&<>'"]/g, (c) => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;'}[c])); }
    function pretty(value) { try { return JSON.stringify(value ?? {}, null, 2); } catch (_) { return String(value); } }
    function setStatus(text, error) { status.textContent = text || ''; status.className = 'status' + (error ? ' error' : ''); }
    function addMessage(role, content, meta) {
      empty.hidden = true;
      const item = document.createElement('article');
      item.className = 'message ' + role;
      item.innerHTML = '<div class="avatar" aria-hidden="true">' + (role === 'user' ? 'YOU' : 'AI') + '</div><div><div class="bubble">' + escapeHtml(content) + '</div>' + (meta ? '<div class="meta">' + escapeHtml(meta) + '</div>' : '') + '</div>';
      messages.appendChild(item);
      item.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
    function addTrace(events, state, transcriptFile) {
      if (!events || !events.length) return;
      const trace = document.createElement('section');
      trace.className = 'trace';
      let html = '<div class="trace-title"><span>Tool trace</span><span>' + escapeHtml(state || 'answered') + '</span></div>';
      events.forEach((event, index) => {
        const result = event && event.result ? event.result : {};
        const failed = Boolean(result && result.error);
        html += '<details class="tool" open><summary>' + (index + 1) + '. ' + escapeHtml(event.tool || 'unknown_tool') + '</summary><pre class="' + (failed ? 'error' : '') + '"><strong>INPUT</strong>\n' + escapeHtml(pretty(event.args)) + '\n\n<strong>RESULT' + (failed ? ' / ERROR' : '') + '</strong>\n' + escapeHtml(pretty(result)) + '</pre></details>';
      });
      if (transcriptFile) html += '<div class="meta">Transcript: ' + escapeHtml(transcriptFile) + '</div>';
      trace.innerHTML = html;
      messages.appendChild(trace);
      trace.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
    async function submitMessage(message) {
      addMessage('user', message, 'just now');
      input.value = '';
      send.disabled = true;
      setStatus('Running the agent and collecting tool evidence…', false);
      try {
        const response = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({session_id: sessionId, message})});
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || 'The request failed.');
        if (payload.status === 'provider_error') {
          addMessage('assistant', payload.error || 'The provider returned an error.', 'provider error');
          setStatus('Provider error — check the local provider setup and transcript.', true);
        } else {
          addMessage('assistant', payload.assistant_text || 'No text response was returned.', payload.status);
          addTrace(payload.tool_events, payload.status, payload.transcript_file);
          setStatus('Transcript saved: ' + payload.transcript_file, false);
        }
      } catch (error) {
        addMessage('assistant', error.message || 'Unexpected UI error.', 'request error');
        setStatus(error.message || 'Unexpected UI error.', true);
      } finally { send.disabled = false; input.focus(); }
    }
    document.getElementById('composer').addEventListener('submit', (event) => { event.preventDefault(); const message = input.value.trim(); if (message) submitMessage(message); });
    document.getElementById('clear').addEventListener('click', () => { sessionId = newSessionId(); messages.innerHTML = ''; messages.appendChild(empty); empty.hidden = false; setStatus('New conversation ready.', false); input.focus(); });
    input.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); document.getElementById('composer').requestSubmit(); } });
  </script>
</body>
</html>
"""


class AppState:
    def __init__(
        self,
        *,
        provider_name: str,
        model: str | None,
        version: str,
        system_prompt_path: Path,
        tools_path: Path,
        transcripts_dir: Path,
        history_window: int,
        max_tool_rounds: int,
    ) -> None:
        self.provider_name = provider_name
        self.version = version
        self.system_prompt_path = system_prompt_path
        self.tools_path = tools_path
        self.transcripts_dir = transcripts_dir
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        self.openai_tools = to_openai_tools(load_tool_declarations(tools_path))
        self.provider = make_provider(provider_name)
        self.model = model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
        self._sessions: dict[str, dict[str, Any]] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._lock = threading.Lock()

    def get_session(self, requested_id: str | None) -> tuple[str, dict[str, Any], threading.Lock]:
        session_id = safe_slug(str(requested_id or ""))[:80] or f"ui_{uuid.uuid4().hex}"
        with self._lock:
            if session_id not in self._sessions:
                transcript_id = f"ui_{safe_slug(self.version)}_{uuid.uuid4().hex[:12]}"
                transcript = {
                    "transcript_id": transcript_id,
                    **artifact_version_dict(self.artifact_version),
                    "provider": self.provider_name,
                    "model": self.model,
                    "system_prompt": str(self.system_prompt_path),
                    "tools": str(self.tools_path),
                    "history_window": self.history_window,
                    "max_tool_rounds": self.max_tool_rounds,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "turns": [],
                }
                path = self.transcripts_dir / f"{transcript_id}.transcript.json"
                self._sessions[session_id] = {"history": [], "transcript": transcript, "path": path}
                self._locks[session_id] = threading.Lock()
            return session_id, self._sessions[session_id], self._locks[session_id]

    def config(self) -> dict[str, Any]:
        return {"provider": self.provider_name, "model": self.model, "version": self.version, "artifact_version": self.artifact_version.artifact_version}


def send_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


class RequestHandler(BaseHTTPRequestHandler):
    state: AppState

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[ui] {self.address_string()} - {format % args}")

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        route = urlparse(self.path).path
        if route == "/":
            body = PAGE.replace("__APP_CONFIG__", json.dumps(self.state.config(), ensure_ascii=False))
            encoded = body.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        if route == "/api/config":
            send_json(self, self.state.config())
            return
        send_json(self, {"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if urlparse(self.path).path != "/api/chat":
            send_json(self, {"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                raise ValueError("Request body is empty or too large.")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            message = str(payload.get("message", "")).strip()
            if not message:
                raise ValueError("Message is required.")
            if len(message) > 6000:
                raise ValueError("Message must be 6000 characters or fewer.")
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            send_json(self, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        session_id, session, session_lock = self.state.get_session(payload.get("session_id"))
        with session_lock:
            started_at = now_iso()
            messages = [
                {"role": "system", "content": self.state.system_prompt},
                *trim_history(session["history"], self.state.history_window),
                {"role": "user", "content": message},
            ]
            try:
                result = run_model_tool_loop(
                    provider=self.state.provider,
                    messages=messages,
                    tools=self.state.openai_tools,
                    model=self.state.model,
                    max_tool_rounds=self.state.max_tool_rounds,
                )
                error = None
            except Exception as exc:  # Preserve provider failures in the transcript.
                result = {"status": "provider_error", "assistant_text": "", "rounds": [], "tool_events": []}
                error = f"{type(exc).__name__}: {exc}"

            turn = {"turn_index": len(session["transcript"]["turns"]) + 1, "started_at": started_at, "user": message, **result, "ended_at": now_iso()}
            if error:
                turn["error"] = error
            session["transcript"]["turns"].append(turn)
            if not error:
                session["history"].append({"role": "user", "content": message})
                session["history"].append({"role": "assistant", "content": result.get("assistant_text", "")})
            write_transcript(session["path"], session["transcript"])

            path = session["path"]
            try:
                transcript_file = str(path.relative_to(ROOT))
            except ValueError:
                transcript_file = str(path)
            response = {
                "session_id": session_id,
                "status": result["status"],
                "assistant_text": result.get("assistant_text") or "",
                "tool_events": result.get("tool_events", []),
                "artifact_version": self.state.artifact_version.artifact_version,
                "transcript_file": transcript_file,
            }
            if error:
                response["error"] = error
                send_json(self, response, HTTPStatus.BAD_GATEWAY)
            else:
                send_json(self, response)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local web UI for the IT Helpdesk agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label, e.g. v3")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = AppState(
        provider_name=args.provider,
        model=args.model,
        version=args.version,
        system_prompt_path=args.system_prompt,
        tools_path=args.tools,
        transcripts_dir=args.transcripts_dir,
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
    )
    RequestHandler.state = state
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler)
    print(f"Northstar Helpdesk UI: http://{args.host}:{args.port}")
    print(f"artifact_version={state.artifact_version.artifact_version}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
