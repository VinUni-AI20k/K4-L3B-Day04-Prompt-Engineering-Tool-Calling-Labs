from __future__ import annotations

import argparse
import json
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote

UI_DIR = Path(__file__).parent
ROOT = UI_DIR.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import (  # noqa: E402  (path must be adjusted first)
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from providers import make_provider  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402

# Static categorisation matching artifacts/tools.yaml's "Core tools" /
# "Optional/advanced tools" comment sections. Kept here only for display —
# never used to change routing or execution behaviour.
CORE_TOOL_NAMES = {
    "clarify",
    "search_kb",
    "check_service_status",
    "inspect_device",
    "lookup_user",
    "format_incident_report",
}

STATE: dict[str, Any] = {}
LOCK = threading.Lock()


def new_transcript(args: argparse.Namespace, artifact_version) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(args.version), safe_slug(args.provider), timestamp])
    transcript_path = args.transcripts_dir / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": args.provider,
        "model": STATE["model"],
        "system_prompt": str(args.system_prompt),
        "tools": str(args.tools),
        "history_window": args.history_window,
        "max_tool_rounds": args.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return {"transcript": transcript, "path": transcript_path}


def init_state(args: argparse.Namespace) -> None:
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(args.tools)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)

    STATE.update({
        "args": args,
        "system_prompt": system_prompt,
        "tool_declarations": tool_declarations,
        "openai_tools": openai_tools,
        "provider": provider,
        "model": model,
        "artifact_version": artifact_version,
        "history": [],
        "turn_index": 0,
    })
    bundle = new_transcript(args, artifact_version)
    STATE["transcript"] = bundle["transcript"]
    STATE["transcript_path"] = bundle["path"]


def meta_payload() -> dict[str, Any]:
    args = STATE["args"]
    tools_view = [
        {
            "name": item["name"],
            "description": item.get("description", ""),
            "category": "core" if item["name"] in CORE_TOOL_NAMES else "optional",
        }
        for item in STATE["tool_declarations"]
    ]
    return {
        "version": args.version,
        "artifact_version": STATE["artifact_version"].artifact_version,
        "provider": args.provider,
        "model": STATE["model"],
        "history_window": args.history_window,
        "max_tool_rounds": args.max_tool_rounds,
        "transcript_id": STATE["transcript"]["transcript_id"],
        "tools": tools_view,
    }


def handle_chat(message: str) -> dict[str, Any]:
    args = STATE["args"]
    with LOCK:
        STATE["turn_index"] += 1
        turn_index = STATE["turn_index"]
        messages = [
            {"role": "system", "content": STATE["system_prompt"]},
            *trim_history(STATE["history"], args.history_window),
            {"role": "user", "content": message},
        ]
        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": message,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        try:
            result = run_model_tool_loop(
                provider=STATE["provider"],
                messages=messages,
                tools=STATE["openai_tools"],
                model=args.model,
                max_tool_rounds=args.max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            STATE["history"].append({"role": "user", "content": message})
            STATE["history"].append({"role": "assistant", "content": assistant_text})
        except Exception as exc:  # keep UI robust; surface the error, do not hide it
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })

        turn_record["ended_at"] = now_iso()
        STATE["transcript"]["turns"].append(turn_record)
        write_transcript(STATE["transcript_path"], STATE["transcript"])
        return turn_record


def handle_reset() -> dict[str, Any]:
    with LOCK:
        STATE["history"] = []
        STATE["turn_index"] = 0
        bundle = new_transcript(STATE["args"], STATE["artifact_version"])
        STATE["transcript"] = bundle["transcript"]
        STATE["transcript_path"] = bundle["path"]
        write_transcript(STATE["transcript_path"], STATE["transcript"])
        return meta_payload()


def list_transcripts() -> list[dict[str, Any]]:
    args = STATE["args"]
    sources = [("live", args.transcripts_dir), ("sample", ROOT / "samples" / "transcripts")]
    items: list[dict[str, Any]] = []
    for source, directory in sources:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            items.append({
                "id": f"{source}:{path.name}",
                "source": source,
                "transcript_id": data.get("transcript_id", path.stem),
                "version": data.get("version", "?"),
                "artifact_version": data.get("artifact_version", ""),
                "provider": data.get("provider", ""),
                "model": data.get("model", ""),
                "created_at": data.get("created_at", ""),
                "turns_count": len(data.get("turns", [])),
            })
    items.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return items


def get_transcript(item_id: str) -> dict[str, Any] | None:
    args = STATE["args"]
    if ":" not in item_id:
        return None
    source, filename = item_id.split(":", 1)
    directory = args.transcripts_dir if source == "live" else ROOT / "samples" / "transcripts"
    path = directory / filename
    if not path.exists() or path.resolve().parent != directory.resolve() or path.suffix != ".json":
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_runs() -> list[dict[str, Any]]:
    args = STATE["args"]
    items: list[dict[str, Any]] = []
    if not args.runs_dir.exists():
        return items
    for path in sorted(args.runs_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        items.append({
            "run_id": data.get("run_id", path.stem),
            "version": data.get("version", "?"),
            "suite": data.get("suite", ""),
            "provider": data.get("provider", ""),
            "model": data.get("model", ""),
            "generated_at": data.get("generated_at", ""),
            "summary": data.get("summary", {}),
        })
    items.sort(key=lambda item: (item.get("version") or "", item.get("generated_at") or ""))
    return items


def get_run(run_id: str) -> dict[str, Any] | None:
    args = STATE["args"]
    safe = safe_slug(run_id)
    path = args.runs_dir / f"{safe}.json"
    if not path.exists() or path.parent.resolve() != args.runs_dir.resolve():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # quieter default logging
        sys.stderr.write("[ui] " + (fmt % args) + "\n")

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, filename: str) -> None:
        path = UI_DIR / filename
        if not path.exists():
            self._send_json({"error": "not_found"}, 404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path in ("/", "/index.html"):
                self._send_static("index.html")
            elif path in ("/app.js", "/styles.css"):
                self._send_static(path.lstrip("/"))
            elif path == "/api/meta":
                self._send_json(meta_payload())
            elif path == "/api/transcripts":
                self._send_json({"items": list_transcripts()})
            elif path.startswith("/api/transcripts/"):
                item_id = unquote(path[len("/api/transcripts/"):])
                data = get_transcript(item_id)
                if data is None:
                    self._send_json({"error": "not_found"}, 404)
                else:
                    self._send_json(data)
            elif path == "/api/runs":
                self._send_json({"items": list_runs()})
            elif path.startswith("/api/runs/"):
                run_id = unquote(path[len("/api/runs/"):])
                data = get_run(run_id)
                if data is None:
                    self._send_json({"error": "not_found"}, 404)
                else:
                    self._send_json(data)
            else:
                self._send_json({"error": "not_found"}, 404)
        except Exception as exc:  # keep server alive; surface the failure
            self._send_json({"error": type(exc).__name__, "message": str(exc)}, 500)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            self._send_json({"error": "invalid_json"}, 400)
            return
        try:
            if parsed.path == "/api/chat":
                message = (body.get("message") or "").strip()
                if not message:
                    self._send_json({"error": "empty_message"}, 400)
                    return
                self._send_json(handle_chat(message))
            elif parsed.path == "/api/reset":
                self._send_json(handle_reset())
            else:
                self._send_json({"error": "not_found"}, 404)
        except Exception as exc:
            self._send_json({"error": type(exc).__name__, "message": str(exc)}, 500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local web UI for the Day04 Helpdesk Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label shown in the UI, e.g. v0, v1, v2, v3.")
    parser.add_argument("--system-prompt", type=Path, default=ROOT / "artifacts" / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    args.transcripts_dir.mkdir(parents=True, exist_ok=True)
    init_state(args)
    write_transcript(STATE["transcript_path"], STATE["transcript"])

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Day04 Helpdesk UI — version={args.version} artifact_version={STATE['artifact_version'].artifact_version}")
    print(f"Provider={args.provider} model={STATE['model']}")
    print(f"Transcript: {STATE['transcript_path']}")
    print(f"Listening on http://127.0.0.1:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
