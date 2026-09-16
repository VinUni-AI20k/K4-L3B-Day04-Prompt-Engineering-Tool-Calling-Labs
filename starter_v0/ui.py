from __future__ import annotations

import argparse
import json
import mimetypes
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import (
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


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
STATIC_DIR = ROOT / "ui_static"
load_lab_env(ROOT)

STATUS_LABELS = {
    "answered": "Đã trả lời",
    "waiting_for_user": "Chờ bạn bổ sung / xác nhận",
    "provider_error": "Lỗi provider — xem chi tiết, không ẩn",
    "max_tool_rounds": "Dừng vì quá số vòng tool",
    "started": "Đang xử lý",
}


class ChatSession:
    def __init__(
        self,
        *,
        provider_name: str,
        version: str,
        model: str | None,
        history_window: int,
        max_tool_rounds: int,
        transcripts_dir: Path,
    ) -> None:
        self.lock = threading.Lock()
        self.provider_name = provider_name
        self.version = version
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.transcripts_dir = transcripts_dir
        self.system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        self.tools_path = ARTIFACTS_DIR / "tools.yaml"
        self.system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
        declarations = load_tool_declarations(self.tools_path)
        self.openai_tools = to_openai_tools(declarations)
        self.provider = make_provider(provider_name)
        self.model = model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(version, self.system_prompt_path, self.tools_path)
        self.history: list[dict[str, str]] = []
        self.turn_index = 0
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        self.transcript_id = "_".join([
            safe_slug(version),
            safe_slug(provider_name),
            "ui",
            timestamp,
        ])
        self.transcript_path = transcripts_dir / f"{self.transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": provider_name,
            "model": self.model,
            "system_prompt": str(self.system_prompt_path),
            "tools": str(self.tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "ui": "web",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        write_transcript(self.transcript_path, self.transcript)

    def meta(self) -> dict[str, Any]:
        return {
            "transcript_id": self.transcript_id,
            "transcript_path": str(self.transcript_path),
            "provider": self.provider_name,
            "model": self.model,
            "version": self.version,
            "artifact_version": self.artifact_version.artifact_version,
            "prompt_hash": self.artifact_version.prompt_hash,
            "tools_hash": self.artifact_version.tools_hash,
            "history_window": self.history_window,
            "max_tool_rounds": self.max_tool_rounds,
            "turn_count": self.turn_index,
            "status_labels": STATUS_LABELS,
        }

    def reset(self) -> dict[str, Any]:
        with self.lock:
            self.history = []
            self.turn_index = 0
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
            self.transcript_id = "_".join([
                safe_slug(self.version),
                safe_slug(self.provider_name),
                "ui",
                timestamp,
            ])
            self.transcript_path = self.transcripts_dir / f"{self.transcript_id}.transcript.json"
            self.transcript = {
                "transcript_id": self.transcript_id,
                **artifact_version_dict(self.artifact_version),
                "provider": self.provider_name,
                "model": self.model,
                "system_prompt": str(self.system_prompt_path),
                "tools": str(self.tools_path),
                "history_window": self.history_window,
                "max_tool_rounds": self.max_tool_rounds,
                "ui": "web",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "turns": [],
            }
            write_transcript(self.transcript_path, self.transcript)
            return self.meta()

    def chat(self, user_text: str) -> dict[str, Any]:
        user_text = (user_text or "").strip()
        if not user_text:
            return {"ok": False, "error": "empty_message"}

        with self.lock:
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
                    verbose=False,
                )
                turn_record.update(result)
                assistant_text = result.get("assistant_text") or ""
                self.history.append({"role": "user", "content": user_text})
                self.history.append({"role": "assistant", "content": assistant_text})
            except Exception as exc:
                turn_record.update({
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {str(exc)}",
                    "assistant_text": f"Lỗi provider: {type(exc).__name__}: {exc}",
                })
            turn_record["ended_at"] = now_iso()
            turn_record["status_label"] = STATUS_LABELS.get(turn_record.get("status", ""), turn_record.get("status"))
            self.transcript["turns"].append(turn_record)
            write_transcript(self.transcript_path, self.transcript)
            return {
                "ok": True,
                "turn": turn_record,
                "meta": self.meta(),
            }


SESSION: ChatSession | None = None


def json_bytes(payload: Any, status: int = 200) -> tuple[int, bytes, str]:
    body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    return status, body, "application/json; charset=utf-8"


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthstarHelpdeskUI/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            return self._serve_static("index.html")
        if path.startswith("/static/"):
            return self._serve_static(path[len("/static/"):])
        if path == "/api/meta":
            assert SESSION is not None
            status, body, ctype = json_bytes({"ok": True, "meta": SESSION.meta()})
            return self._send(status, body, ctype)
        if path == "/api/transcript":
            assert SESSION is not None
            status, body, ctype = json_bytes({"ok": True, "transcript": SESSION.transcript, "path": str(SESSION.transcript_path)})
            return self._send(status, body, ctype)
        self._send(404, b'{"ok":false,"error":"not_found"}', "application/json")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        assert SESSION is not None
        try:
            payload = self._read_json()
        except Exception as exc:
            status, body, ctype = json_bytes({"ok": False, "error": str(exc)}, 400)
            return self._send(status, body, ctype)

        if path == "/api/chat":
            result = SESSION.chat(str(payload.get("message") or ""))
            code = 200 if result.get("ok") else 400
            status, body, ctype = json_bytes(result, code)
            return self._send(status, body, ctype)
        if path == "/api/reset":
            meta = SESSION.reset()
            status, body, ctype = json_bytes({"ok": True, "meta": meta})
            return self._send(status, body, ctype)
        self._send(404, b'{"ok":false,"error":"not_found"}', "application/json")

    def _serve_static(self, relative: str) -> None:
        target = (STATIC_DIR / relative).resolve()
        if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
            self._send(403, b"forbidden", "text/plain")
            return
        if not target.is_file():
            self._send(404, b"not found", "text/plain")
            return
        data = target.read_bytes()
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix == ".js":
            ctype = "application/javascript; charset=utf-8"
        elif target.suffix == ".css":
            ctype = "text/css; charset=utf-8"
        elif target.suffix == ".html":
            ctype = "text/html; charset=utf-8"
        self._send(200, data, ctype)


def main() -> None:
    global SESSION
    parser = argparse.ArgumentParser(description="Web UI for the IT Helpdesk Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], default="openrouter")
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="v3")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    args = parser.parse_args()

    SESSION = ChatSession(
        provider_name=args.provider,
        version=args.version,
        model=args.model,
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
        transcripts_dir=args.transcripts_dir,
    )
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Northstar Labs Helpdesk UI")
    print(f"artifact_version={SESSION.artifact_version.artifact_version}")
    print(f"Open http://{args.host}:{args.port}")
    print("UI shows: version, user/assistant text, tool name, args, result/error, status.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
