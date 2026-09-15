from __future__ import annotations

import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from session_store import PostgresSessionStore
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
UI_DIR = ROOT / "ui"
load_lab_env(ROOT)


class HelpdeskService:
    def __init__(self) -> None:
        self.prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        self.tools_path = ARTIFACTS_DIR / "tools.yaml"
        self.prompt = self.prompt_path.read_text(encoding="utf-8")
        self.declarations = load_tool_declarations(self.tools_path)
        self.tools = to_openai_tools(self.declarations)
        self.provider = make_provider("gemini")
        self.model = os.getenv("GEMINI_MODEL", self.provider.default_model)
        version = os.getenv("HELPDESK_VERSION", "v9")
        self.artifact = build_artifact_version(version, self.prompt_path, self.tools_path)
        self.lock = threading.Lock()

    def respond(self, user_id: str, session_id: str, text: str, history: list[dict[str, str]]) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": self.prompt},
            *history[-10:],
            {"role": "user", "content": text},
        ]
        loop_result = run_model_tool_loop(
            provider=self.provider,
            messages=messages,
            tools=self.tools,
            model=self.model,
            max_tool_rounds=4,
        )
        reply = loop_result["assistant_text"]
        return {
            "reply": reply,
            "tool_calls": [call for round_item in loop_result["rounds"] for call in round_item["tool_calls"]],
            "tool_events": loop_result["tool_events"],
            "version": self.artifact.artifact_version,
            "model": self.model,
            "session_id": session_id,
            "user_id": user_id,
        }


SERVICE = HelpdeskService()


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", os.getenv("HELPDESK_UI_CORS", "*"))
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"status": "ok", "provider": "gemini", "version": SERVICE.artifact.artifact_version})
            return
        if path == "/api/sessions":
            query = dict(item.split("=", 1) for item in urlparse(self.path).query.split("&") if "=" in item)
            user_id = query.get("user_id", "").strip()
            if not user_id:
                self._json(400, {"error": "user_id is required"})
                return
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                self._json(200, {"sessions": []})
                return
            try:
                with PostgresSessionStore(database_url) as store:
                    self._json(200, {"sessions": store.list_sessions(user_id)})
            except RuntimeError as exc:
                self._json(503, {"error": str(exc)})
            return
        if path == "/api/history":
            query = dict(item.split("=", 1) for item in urlparse(self.path).query.split("&") if "=" in item)
            user_id = query.get("user_id", "").strip()
            session_id = query.get("session_id", "").strip()
            if not user_id or not session_id:
                self._json(400, {"error": "user_id and session_id are required"})
                return
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                self._json(200, {"messages": []})
                return
            try:
                with PostgresSessionStore(database_url) as store:
                    self._json(200, {"messages": store.load_messages(user_id, session_id)})
            except RuntimeError as exc:
                self._json(503, {"error": str(exc)})
            return
        if path != "/":
            self._json(404, {"error": "not_found"})
            return
        body = (UI_DIR / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", os.getenv("HELPDESK_UI_CORS", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            user_id = str(payload.get("user_id", "")).strip()
            session_id = str(payload.get("session_id") or uuid.uuid4()).strip()
            text = str(payload.get("message", "")).strip()
            history = payload.get("history") or []
            if not user_id or not text:
                self._json(400, {"error": "user_id and message are required"})
                return
            result = SERVICE.respond(user_id, session_id, text, history)
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                with PostgresSessionStore(database_url) as store:
                    store.start_session(user_id, session_id, provider="gemini", model=SERVICE.model)
                    store.append_message(user_id, session_id, "user", text)
                    store.append_message(user_id, session_id, "assistant", result["reply"])
            self._json(200, result)
        except Exception as exc:
            self._json(500, {"error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    host = os.getenv("HELPDESK_UI_HOST", "127.0.0.1")
    port = int(os.getenv("HELPDESK_UI_PORT", "8000"))
    print(f"Helpdesk UI: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
