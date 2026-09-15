from __future__ import annotations

import argparse
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# The web UI reuses the CLI tool loop on purpose: chat.py and the browser must
# produce the same behaviour and the same transcript shape, otherwise UI
# evidence cannot be compared with CLI evidence.
from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
WEB_DIR = ROOT / "web"
load_lab_env(ROOT)


@dataclass
class Settings:
    provider_name: str
    version: str
    model: str | None
    system_prompt_path: Path
    tools_path: Path
    transcripts_dir: Path
    history_window: int
    max_tool_rounds: int


@dataclass
class Session:
    session_id: str
    created_at: str
    transcript_path: Path
    transcript: dict[str, Any]
    history: list[dict[str, str]] = field(default_factory=list)
    turn_index: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class MessageIn(BaseModel):
    message: str


def load_ui_config() -> dict[str, Any]:
    path = WEB_DIR / "ui.config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # a broken config must not take the whole UI down
        return {"config_error": f"{type(exc).__name__}: {exc}"}


def create_app(settings: Settings) -> FastAPI:
    system_prompt = settings.system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(settings.tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(settings.provider_name)
    selected_model = settings.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(
        settings.version, settings.system_prompt_path, settings.tools_path
    )

    sessions: dict[str, Session] = {}
    sessions_lock = threading.Lock()

    app = FastAPI(title="PC Sales Agent Console", version=artifact_version.artifact_version)

    def meta_payload() -> dict[str, Any]:
        return {
            **artifact_version_dict(artifact_version),
            "provider": settings.provider_name,
            "model": selected_model,
            "system_prompt": str(settings.system_prompt_path),
            "system_prompt_name": settings.system_prompt_path.name,
            "tools_file": str(settings.tools_path),
            "tools_file_name": settings.tools_path.name,
            "history_window": settings.history_window,
            "max_tool_rounds": settings.max_tool_rounds,
            "tools": [
                {
                    "name": item["name"],
                    "description": item.get("description", ""),
                    "parameters": item.get("parameters", {}),
                    "required": item.get("parameters", {}).get("required", []),
                }
                for item in tool_declarations
            ],
            "ui": load_ui_config(),
            "server_time": now_iso(),
        }

    def new_session() -> Session:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        session_id = "_".join([safe_slug(settings.version), safe_slug(settings.provider_name), timestamp])
        transcript_path = settings.transcripts_dir / f"{session_id}.transcript.json"
        transcript: dict[str, Any] = {
            "transcript_id": session_id,
            **artifact_version_dict(artifact_version),
            "interface": "web_ui",
            "provider": settings.provider_name,
            "model": selected_model,
            "system_prompt": str(settings.system_prompt_path),
            "tools": str(settings.tools_path),
            "history_window": settings.history_window,
            "max_tool_rounds": settings.max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        session = Session(
            session_id=session_id,
            created_at=now_iso(),
            transcript_path=transcript_path,
            transcript=transcript,
        )
        write_transcript(transcript_path, transcript)
        with sessions_lock:
            sessions[session_id] = session
        return session

    def get_session(session_id: str) -> Session:
        with sessions_lock:
            session = sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail=f"Unknown session_id: {session_id}")
        return session

    def session_summary(session: Session) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "updated_at": session.transcript.get("updated_at"),
            "turn_count": len(session.transcript["turns"]),
            "transcript_path": str(session.transcript_path),
        }

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "artifact_version": artifact_version.artifact_version}

    @app.get("/api/meta")
    def meta() -> dict[str, Any]:
        return meta_payload()

    @app.post("/api/sessions")
    def create_session() -> dict[str, Any]:
        session = new_session()
        return {**session_summary(session), "meta": meta_payload()}

    @app.get("/api/sessions")
    def list_sessions() -> dict[str, Any]:
        with sessions_lock:
            items = [session_summary(item) for item in sessions.values()]
        items.sort(key=lambda item: item["created_at"], reverse=True)
        return {"sessions": items}

    @app.get("/api/sessions/{session_id}")
    def read_session(session_id: str) -> dict[str, Any]:
        return get_session(session_id).transcript

    @app.post("/api/sessions/{session_id}/messages")
    def post_message(session_id: str, payload: MessageIn) -> dict[str, Any]:
        session = get_session(session_id)
        user_text = (payload.message or "").strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="Empty message")

        with session.lock:
            session.turn_index += 1
            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(session.history, settings.history_window),
                {"role": "user", "content": user_text},
            ]
            turn_record: dict[str, Any] = {
                "turn_index": session.turn_index,
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }

            started = time.perf_counter()
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=settings.model,
                    max_tool_rounds=settings.max_tool_rounds,
                )
                turn_record.update(result)
                session.history.append({"role": "user", "content": user_text})
                session.history.append({"role": "assistant", "content": result["assistant_text"]})
            except Exception as exc:
                # Provider failures stay visible in the UI instead of being hidden;
                # a silent failure would make transcript evidence misleading.
                turn_record.update({
                    "status": "provider_error",
                    "assistant_text": None,
                    "error": f"{type(exc).__name__}: {exc}",
                })

            turn_record["latency_ms"] = int((time.perf_counter() - started) * 1000)
            turn_record["ended_at"] = now_iso()
            session.transcript["turns"].append(turn_record)
            write_transcript(session.transcript_path, session.transcript)

        return {
            "session_id": session.session_id,
            "artifact_version": artifact_version.artifact_version,
            "version": settings.version,
            "transcript_path": str(session.transcript_path),
            "turn": turn_record,
        }

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Web UI backend for the agent chat console.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label shown in the UI, e.g. v0, v1.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    import uvicorn

    args = parse_args()
    settings = Settings(
        provider_name=args.provider,
        version=args.version,
        model=args.model,
        system_prompt_path=args.system_prompt,
        tools_path=args.tools,
        transcripts_dir=args.transcripts_dir,
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
    )
    app = create_app(settings)
    print(f"UI:  http://{args.host}:{args.port}/")
    print(f"API: http://{args.host}:{args.port}/api/meta")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
