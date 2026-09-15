from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from chat import now_iso, run_model_tool_loop, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
WEB_DIR = ROOT / "web"
load_lab_env(ROOT)

TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

# Every version selectable in the UI. "v3" and "final" both point at the
# same content today (artifacts/system_prompt.md was set to the v3 text),
# kept as separate entries so the dropdown always has a "current" pointer
# even if the team keeps iterating past v3 without renaming files.
VERSION_FILES: dict[str, Path] = {
    "v0": ARTIFACTS_DIR / "system_prompt_v0.md",
    "v1": ARTIFACTS_DIR / "system_prompt_v1.md",
    "v2": ARTIFACTS_DIR / "system_prompt_v2.md",
    "v3": ARTIFACTS_DIR / "system_prompt_v3.md",
    "final": ARTIFACTS_DIR / "system_prompt.md",
}


class AppState:
    def __init__(self, provider_name: str, model: str | None) -> None:
        self.provider_name = provider_name
        self.model = model
        self.provider = make_provider(provider_name)
        self.tool_declarations = load_tool_declarations(TOOLS_PATH)
        self.openai_tools = to_openai_tools(self.tool_declarations)
        self.tools_hash = build_artifact_version("_", next(iter(VERSION_FILES.values())), TOOLS_PATH).tools_hash


STATE: AppState | None = None


def available_versions() -> list[dict[str, Any]]:
    out = []
    for key, path in VERSION_FILES.items():
        if not path.exists():
            continue
        av = build_artifact_version(key, path, TOOLS_PATH)
        out.append({"key": key, "artifact_version": av.artifact_version})
    return out


def run_turn(version_key: str, history: list[dict[str, str]], user_text: str) -> dict[str, Any]:
    assert STATE is not None
    prompt_path = VERSION_FILES.get(version_key)
    if prompt_path is None or not prompt_path.exists():
        return {"status": "error", "error": f"Unknown version '{version_key}'"}

    system_prompt = prompt_path.read_text(encoding="utf-8")
    artifact_version = build_artifact_version(version_key, prompt_path, TOOLS_PATH)
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_text},
    ]

    result = run_model_tool_loop(
        provider=STATE.provider,
        messages=messages,
        tools=STATE.openai_tools,
        model=STATE.model,
        max_tool_rounds=4,
    )
    result["artifact_version"] = artifact_version.artifact_version
    result["version_key"] = version_key
    result["provider"] = STATE.provider_name
    result["model"] = STATE.model or getattr(STATE.provider, "default_model", None)
    return result


def append_transcript(conversation_id: str, version_key: str, turn_index: int, user_text: str, result: dict[str, Any]) -> None:
    path = TRANSCRIPTS_DIR / f"webui_{conversation_id}.transcript.json"
    if path.exists():
        transcript = json.loads(path.read_text(encoding="utf-8"))
    else:
        transcript = {
            "transcript_id": f"webui_{conversation_id}",
            "created_at": now_iso(),
            "turns": [],
        }
    transcript["turns"].append({
        "turn_index": turn_index,
        "started_at": now_iso(),
        "version_key": version_key,
        "artifact_version": result.get("artifact_version"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "user": user_text,
        "status": result.get("status"),
        "assistant_text": result.get("assistant_text"),
        "rounds": result.get("rounds"),
        "tool_events": result.get("tool_events"),
        "ended_at": now_iso(),
    })
    write_transcript(path, transcript)


class Handler(BaseHTTPRequestHandler):
    server_version = "VietTravelWebUI/1.0"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        print(f"[webui] {self.address_string()} {format % args}")

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        if self.path in {"/", "/index.html"}:
            self._send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return
        if self.path == "/app.js":
            self._send_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        if self.path == "/api/versions":
            self._send_json({"versions": available_versions()})
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.path != "/api/chat":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            version_key = str(payload["version"])
            user_text = str(payload["message"])
            history = payload.get("history") or []
            conversation_id = str(payload.get("conversation_id") or uuid.uuid4())
            turn_index = int(payload.get("turn_index") or 1)
        except Exception as exc:
            self._send_json({"status": "error", "error": f"Bad request: {exc}"}, status=400)
            return

        try:
            result = run_turn(version_key, history, user_text)
        except Exception as exc:
            result = {"status": "provider_error", "error": f"{type(exc).__name__}: {exc}", "assistant_text": None}

        try:
            append_transcript(conversation_id, version_key, turn_index, user_text, result)
        except Exception as exc:
            print(f"[webui] transcript write failed: {exc}")

        result["conversation_id"] = conversation_id
        self._send_json(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local chat UI for the VietTravel agent.")
    parser.add_argument("--provider", choices=["openai", "openrouter", "anthropic", "gemini"], default="openai")
    parser.add_argument("--model", default=None)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    global STATE
    STATE = AppState(args.provider, args.model)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"VietTravel chat UI: http://127.0.0.1:{args.port}  (provider={args.provider})")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
