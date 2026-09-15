from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from session_store import PostgresSessionStore
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
UI_DIR = ROOT / "ui"
load_lab_env(ROOT)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=12000)
    session_id: str | None = Field(default=None, max_length=120)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    request_id: str
    user_id: str
    session_id: str
    reply: str
    tool_calls: list[dict[str, Any]]
    tool_events: list[dict[str, Any]]
    model: str
    artifact_version: str


class HelpdeskRuntime:
    def __init__(self) -> None:
        self.prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        self.tools_path = ARTIFACTS_DIR / "tools.yaml"
        self.prompt = self.prompt_path.read_text(encoding="utf-8")
        self.tools = to_openai_tools(load_tool_declarations(self.tools_path))
        self.provider = make_provider("gemini")
        self.model = os.getenv("GEMINI_MODEL", self.provider.default_model)
        self.artifact = build_artifact_version(
            os.getenv("HELPDESK_VERSION", "v9"), self.prompt_path, self.tools_path
        )

    def answer(self, request: ChatRequest, session_id: str) -> ChatResponse:
        messages = [
            {"role": "system", "content": self.prompt},
            *request.history[-10:],
            {"role": "user", "content": request.message},
        ]
        result = run_model_tool_loop(
            provider=self.provider,
            messages=messages,
            tools=self.tools,
            model=self.model,
            max_tool_rounds=4,
        )
        tool_calls = [
            call
            for round_item in result["rounds"]
            for call in round_item.get("tool_calls", [])
        ]
        return ChatResponse(
            request_id=str(uuid.uuid4()),
            user_id=request.user_id,
            session_id=session_id,
            reply=result.get("assistant_text", ""),
            tool_calls=tool_calls,
            tool_events=result.get("tool_events", []),
            model=self.model,
            artifact_version=self.artifact.artifact_version,
        )

    def persist(self, request: ChatRequest, response: ChatResponse) -> None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return
        with PostgresSessionStore(database_url) as store:
            store.start_session(
                request.user_id,
                response.session_id,
                provider="gemini",
                model=self.model,
            )
            store.append_message(request.user_id, response.session_id, "user", request.message)
            store.append_message(request.user_id, response.session_id, "assistant", response.reply)


app = FastAPI(
    title="Northstar IT Helpdesk API",
    version="1.0.0",
    description="Gemini tool-calling IT Helpdesk with SSE streaming and PostgreSQL sessions.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("HELPDESK_API_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
runtime = HelpdeskRuntime()


def sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_response(response: ChatResponse) -> AsyncIterator[str]:
    yield sse("start", {
        "request_id": response.request_id,
        "user_id": response.user_id,
        "session_id": response.session_id,
        "model": response.model,
        "artifact_version": response.artifact_version,
    })
    for call in response.tool_calls:
        yield sse("tool_call", {"request_id": response.request_id, **call})
    for event in response.tool_events:
        yield sse("tool_result", {"request_id": response.request_id, **event})
    words = response.reply.split(" ") if response.reply else []
    for index, word in enumerate(words):
        await asyncio.sleep(0)
        yield sse("token", {
            "request_id": response.request_id,
            "index": index,
            "text": f"{word} " if index < len(words) - 1 else word,
        })
    yield sse("done", {
        "request_id": response.request_id,
        "reply": response.reply,
        "tool_calls": response.tool_calls,
        "tool_events": response.tool_events,
        "artifact_version": response.artifact_version,
    })


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "provider": "gemini",
        "model": runtime.model,
        "artifact_version": runtime.artifact.artifact_version,
    }


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.post("/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    try:
        response = runtime.answer(request, session_id)
        runtime.persist(request, response)
        return response
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent request failed: {type(exc).__name__}: {exc}") from exc


@app.post("/v1/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    session_id = request.session_id or str(uuid.uuid4())
    try:
        response = await asyncio.to_thread(runtime.answer, request, session_id)
        await asyncio.to_thread(runtime.persist, request, response)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent request failed: {type(exc).__name__}: {exc}") from exc
    return StreamingResponse(
        stream_response(response),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/v1/sessions")
def sessions(user_id: str = Query(min_length=1, max_length=120)) -> dict[str, Any]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"user_id": user_id, "sessions": []}
    try:
        with PostgresSessionStore(database_url) as store:
            return {"user_id": user_id, "sessions": store.list_sessions(user_id)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/v1/sessions/{session_id}/messages")
def messages(session_id: str, user_id: str = Query(min_length=1, max_length=120)) -> dict[str, Any]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"user_id": user_id, "session_id": session_id, "messages": []}
    try:
        with PostgresSessionStore(database_url) as store:
            return {
                "user_id": user_id,
                "session_id": session_id,
                "messages": store.load_messages(user_id, session_id),
            }
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/openapi.json", include_in_schema=False)
def openapi_json() -> JSONResponse:
    return JSONResponse(app.openapi())
