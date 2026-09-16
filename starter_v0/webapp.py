from __future__ import annotations

import argparse
import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
WEBAPP_DIR = ROOT / "webapp"
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]
VERSIONS = ["v0", "v1", "v2", "v3"]

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}

SESSIONS: dict[str, dict[str, Any]] = {}
SESSIONS_LOCK = threading.Lock()
    

def create_session(payload: dict[str, Any]) -> dict[str, Any]:
    provider_name = payload.get("provider") or "openrouter"
    if provider_name not in PROVIDERS:
        raise ValueError(f"provider phải là một trong {PROVIDERS}")
    version = safe_slug(str(payload.get("version") or "v3"))
    model = (payload.get("model") or "").strip() or None
    history_window = int(payload.get("history_window") or 5)
    max_tool_rounds = int(payload.get("max_tool_rounds") or 4)

    system_prompt_path = Path(payload.get("system_prompt") or ARTIFACTS_DIR / "system_prompt.md")
    tools_path = Path(payload.get("tools") or ARTIFACTS_DIR / "tools.yaml")
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(tools_path))

    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "web_" + "_".join([version, safe_slug(provider_name), timestamp])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        "source": "webapp",
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    session = {
        "session_id": transcript_id,
        "provider_name": provider_name,
        "provider": provider,
        "model": model,
        "system_prompt": system_prompt,
        "openai_tools": openai_tools,
        "history": [],
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "transcript": transcript,
        "transcript_path": transcript_path,
        "turn_index": 0,
    }
    with SESSIONS_LOCK:
        SESSIONS[transcript_id] = session
    write_transcript(transcript_path, transcript)
    return session_info(session)


def session_info(session: dict[str, Any]) -> dict[str, Any]:
    transcript = session["transcript"]
    return {
        "session_id": session["session_id"],
        "provider": session["provider_name"],
        "model": transcript["model"],
        "version": transcript["version"],
        "artifact_version": transcript["artifact_version"],
        "transcript_id": transcript["transcript_id"],
        "transcript_path": str(session["transcript_path"]),
        "history_window": session["history_window"],
        "max_tool_rounds": session["max_tool_rounds"],
        "turns": len(transcript["turns"]),
    }


def handle_chat(payload: dict[str, Any]) -> dict[str, Any]:
    session_id = payload.get("session_id") or ""
    with SESSIONS_LOCK:
        session = SESSIONS.get(session_id)
    if session is None:
        raise LookupError("Phiên không tồn tại. Hãy bắt đầu phiên mới.")

    user_text = str(payload.get("message") or "").strip()
    if not user_text:
        raise ValueError("Tin nhắn trống.")

    session["turn_index"] += 1
    turn_index = session["turn_index"]
    messages = [
        {"role": "system", "content": session["system_prompt"]},
        *trim_history(session["history"], session["history_window"]),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=session["provider"],
            messages=messages,
            tools=session["openai_tools"],
            model=session["model"],
            max_tool_rounds=session["max_tool_rounds"],
        )
        turn_record.update(result)
        session["history"].append({"role": "user", "content": user_text})
        session["history"].append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {str(exc)}",
        })

    turn_record["ended_at"] = now_iso()
    session["transcript"]["turns"].append(turn_record)
    write_transcript(session["transcript_path"], session["transcript"])
    return {"turn": turn_record, "session": session_info(session)}


class WebappHandler(BaseHTTPRequestHandler):
    server_version = "Helpdesk/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[web] {self.address_string()} {fmt % args}")

    def _send_json(self, status: int, data: Any) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            self._send_json(200, {"ok": True})
            return
        if path in {"/", "/index.html"}:
            self._serve_static(WEBAPP_DIR / "index.html")
            return
        candidate = (WEBAPP_DIR / path.lstrip("/")).resolve()
        if candidate.is_file() and candidate.parent == WEBAPP_DIR.resolve():
            self._serve_static(candidate)
            return
        self._send_json(404, {"error": "not_found"})

    def _serve_static(self, file_path: Path) -> None:
        try:
            body = file_path.read_bytes()
        except OSError:
            self._send_json(404, {"error": "not_found"})
            return
        content_type = CONTENT_TYPES.get(file_path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        try:
            payload = self._read_json()
            if path == "/api/session":
                self._send_json(200, create_session(payload))
                return
            if path == "/api/chat":
                self._send_json(200, handle_chat(payload))
                return
            self._send_json(404, {"error": "not_found"})
        except (ValueError, LookupError) as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": f"{type(exc).__name__}: {str(exc)}"})


def main() -> None:
    parser = argparse.ArgumentParser(description="Web UI for the Helpdesk Agent chat.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), WebappHandler)
    print(f"Helpdesk webapp: http://{args.host}:{args.port}")
    print("Nhấn Ctrl+C để dừng.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng webapp.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
