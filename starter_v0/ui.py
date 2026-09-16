from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

# Ensure starter_v0 is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version, file_hash

load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SAMPLES_TRANSCRIPTS_DIR = ROOT / "samples" / "transcripts"
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"

TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def json_text(value: Any, *, max_chars: int | None = None) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if max_chars is not None and len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json_text(call_summary)}",
    }


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{json_text(events, max_chars=24000)}\n\n"
            "Use only these tool results. If the user asked for an incident report and the findings are ready, "
            "call the reporting tool. Otherwise answer directly, state uncertainty, and give the safest next step."
        ),
    }


# High-fidelity Simulator fallback for offline testing or demonstration
def simulate_helpdesk_agent(user_text: str, history: list[dict[str, str]]) -> tuple[str | None, list[ToolCall]]:
    q = user_text.lower()
    
    # 1. Check for sensitive data in create ticket attempt
    if any(k in q for k in ["mật khẩu", "password", "token", "otp", "key"]):
        if any(k in q for k in ["ticket", "tạo ticket", "yêu cầu"]):
            return None, [ToolCall("create_ticket", {"summary": user_text, "priority": "medium", "confirmed": True})]

    # 2. Check ticket creation without confirmation
    if "tạo ticket" in q or "mở ticket" in q or "create ticket" in q:
        if "xác nhận" in q or "confirm" in q or "đồng ý" in q or "đúng vậy" in q or "yes" in q:
            asset_match = re.search(r"\b(LT|DT|MB|PR|RM)-\d+\b", user_text, re.IGNORECASE)
            asset_id = asset_match.group(0).upper() if asset_match else "LT-204"
            return None, [ToolCall("create_ticket", {"summary": "Hỗ trợ kỹ thuật thiết bị", "priority": "medium", "asset_id": asset_id, "confirmed": True})]
        else:
            return None, [ToolCall("clarify", {"question": "Bạn có chắc chắn muốn tạo ticket với các thông tin trên không? (yes/no)", "response_type": "yes_no"})]

    # 3. Check service status
    if "dịch vụ" in q or "service" in q or "status" in q or "sự cố" in q:
        svc = "vpn"
        for s in ["vpn", "email", "sso", "wifi", "printing"]:
            if s in q:
                svc = s
                break
        env = "staging" if "staging" in q else "production"
        if any(amb in q for amb in ["demo", "qa", "test", "dev"]):
            return None, [ToolCall("clarify", {"question": "Vui lòng chọn môi trường dịch vụ:", "response_type": "choice", "options": ["production", "staging"]})]
        return None, [ToolCall("check_service_status", {"service": svc, "environment": env})]

    # 4. Device inspection
    asset_match = re.search(r"\b(LT|DT|MB|PR|RM)-\d+\b", user_text, re.IGNORECASE)
    if asset_match:
        asset_id = asset_match.group(0).upper()
        check = "all"
        if "vpn" in q:
            check = "vpn"
        elif "mạng" in q or "network" in q:
            check = "network"
        elif "bảo mật" in q or "security" in q:
            check = "security"
        elif "phần cứng" in q or "hardware" in q:
            check = "hardware"
        elif "phần mềm" in q or "software" in q:
            check = "software"
        return None, [ToolCall("inspect_device", {"asset_id": asset_id, "check": check})]

    # 5. Missing asset ID
    if any(k in q for k in ["laptop", "máy tính", "thiết bị", "máy của tôi", "laptop của mình"]) and not asset_match:
        if not ("emp-" in q or "nhân viên" in q):
            return None, [ToolCall("clarify", {"question": "Bạn vui lòng cung cấp mã định danh thiết bị (ví dụ LT-204) để kiểm tra.", "response_type": "text"})]

    # 6. Lookup user
    emp_match = re.search(r"\bEMP-\d+\b", user_text, re.IGNORECASE)
    if emp_match:
        return None, [ToolCall("lookup_user", {"employee_id": emp_match.group(0).upper()})]
    if "nhân viên" in q or "tài khoản" in q or "user" in q or "employee" in q:
        return None, [ToolCall("clarify", {"question": "Bạn vui lòng cung cấp mã nhân viên (ví dụ EMP-1003) để tra cứu.", "response_type": "text"})]

    # 7. KB Search
    if any(k in q for k in ["hướng dẫn", "cách", "cấu hình", "howto", "guide", "kb", "knowledge"]):
        cat = "general"
        if any(e in q for e in ["outlook", "email", "mail"]):
            cat = "email"
        elif any(v in q for v in ["vpn", "kết nối từ xa"]):
            cat = "vpn"
        elif any(w in q for w in ["wifi", "mạng"]):
            cat = "wifi"
        elif any(p in q for p in ["in", "print", "printer"]):
            cat = "printing"
        return None, [ToolCall("search_kb", {"category": cat, "query": user_text})]

    # 8. Policy
    if any(k in q for k in ["chính sách", "quy định", "policy", "tiêu chuẩn"]):
        return None, [ToolCall("policy", {"query": user_text})]

    # Default direct response
    return f"Chào bạn, tôi là trợ lý IT Helpdesk của Northstar Labs. Tôi có thể giúp bạn kiểm tra trạng thái dịch vụ, chẩn đoán thiết bị, tra cứu nhân viên, tìm hướng dẫn nội bộ hoặc tạo ticket.", []


def run_chat_turn(
    *,
    user_text: str,
    history: list[dict[str, str]],
    version: str,
    provider_name: str,
    model_override: str | None = None,
    max_tool_rounds: int = 4,
) -> dict[str, Any]:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    system_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else "You are an IT Helpdesk assistant."
    tool_decls = load_tool_declarations(tools_path) if tools_path.exists() else []
    openai_tools = to_openai_tools(tool_decls)

    turn_record: dict[str, Any] = {
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    # Decide whether to use real provider or simulator
    use_simulator = False
    provider = None

    if provider_name == "simulator":
        use_simulator = True
    else:
        try:
            provider = make_provider(provider_name)
        except Exception as exc:
            print(f"[UI] Provider {provider_name} unavailable: {exc}. Falling back to simulator mode.")
            use_simulator = True

    if use_simulator:
        sim_text, sim_calls = simulate_helpdesk_agent(user_text, history)
        round_1: dict[str, Any] = {
            "round": 1,
            "assistant_text": sim_text,
            "tool_calls": [{"name": c.name, "args": c.args} for c in sim_calls],
            "tool_results": [],
        }
        all_events: list[dict[str, Any]] = []

        if not sim_calls:
            turn_record["rounds"].append(round_1)
            turn_record["status"] = "answered"
            turn_record["assistant_text"] = sim_text or "Đã ghi nhận yêu cầu của bạn."
            turn_record["tool_events"] = []
            turn_record["ended_at"] = now_iso()
            return turn_record

        for call in sim_calls:
            event = execute_tool_call(call)
            round_1["tool_results"].append(event)
            all_events.append(event)

        turn_record["rounds"].append(round_1)
        turn_record["tool_events"] = all_events

        first_event = all_events[0]
        res = first_event.get("result", {})
        if isinstance(res, dict) and res.get("awaiting_user"):
            turn_record["status"] = "waiting_for_user"
            turn_record["assistant_text"] = res.get("question") or "Vui lòng cung cấp thêm thông tin."
        elif isinstance(res, dict) and res.get("error"):
            turn_record["status"] = "tool_error"
            err_msg = res.get("message") or res.get("error")
            turn_record["assistant_text"] = f"Công cụ trả về thông báo lỗi: {err_msg}"
        elif isinstance(res, dict) and res.get("status") == "needs_confirmation":
            turn_record["status"] = "needs_confirmation"
            turn_record["assistant_text"] = f"Cần xác nhận: {res.get('message')}"
        else:
            turn_record["status"] = "answered"
            tool_name = first_event.get("tool", "")
            if tool_name == "search_kb":
                hits = res.get("results", [])
                if not hits:
                    turn_record["assistant_text"] = "Rất tiếc, tôi không tìm thấy bài viết hướng dẫn nào phù hợp trong Knowledge Base."
                else:
                    parts = ["Dưới đây là hướng dẫn tìm thấy từ cơ sở tri thức (Knowledge Base):\n"]
                    for hit in hits:
                        title = hit.get("title", "Bài viết hướng dẫn")
                        content = hit.get("content", "")
                        parts.append(f"📌 **{title}**\n\n{content}")
                    turn_record["assistant_text"] = "\n\n---\n\n".join(parts)
            elif tool_name == "inspect_device":
                asset_id = res.get("asset_id") or first_event.get("args", {}).get("asset_id", "thiết bị")
                turn_record["assistant_text"] = f"Kết quả kiểm tra chi tiết thiết bị **{asset_id}**:\n\n```json\n{json.dumps(res, ensure_ascii=False, indent=2)}\n```"
            elif tool_name == "lookup_user":
                turn_record["assistant_text"] = f"Thông tin nhân viên và thiết bị được cấp:\n\n```json\n{json.dumps(res, ensure_ascii=False, indent=2)}\n```"
            elif tool_name == "check_service_status":
                svc = res.get("service") or first_event.get("args", {}).get("service", "")
                env = res.get("environment") or first_event.get("args", {}).get("environment", "")
                st = res.get("status") or "operational"
                turn_record["assistant_text"] = f"Trạng thái dịch vụ **{svc.upper()}** (môi trường `{env}`): **{st}**."
            elif tool_name == "policy":
                turn_record["assistant_text"] = f"Thông tin quy định & chính sách công ty:\n\n```json\n{json.dumps(res, ensure_ascii=False, indent=2)}\n```"
            else:
                turn_record["assistant_text"] = f"Đã thực thi công cụ `{tool_name}` thành công."

        turn_record["ended_at"] = now_iso()
        return turn_record

    # Live Provider Path
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            *history[-10:],
            {"role": "user", "content": user_text},
        ]
        
        rounds: list[dict[str, Any]] = []
        all_tool_events: list[dict[str, Any]] = []
        working_messages = list(messages)
        final_text = ""
        status = "answered"

        for round_idx in range(1, max_tool_rounds + 1):
            response = provider.complete(working_messages, openai_tools, model=model_override, temperature=0.0)
            calls = response.tool_calls
            round_rec: dict[str, Any] = {
                "round": round_idx,
                "assistant_text": response.text,
                "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
                "tool_results": [],
            }

            if not calls:
                rounds.append(round_rec)
                final_text = response.text or ""
                status = "answered"
                break

            working_messages.append(assistant_tool_message(response.text, calls))
            non_clarify: list[dict[str, Any]] = []

            for call in calls:
                event = execute_tool_call(call)
                round_rec["tool_results"].append(event)
                all_tool_events.append(event)

                res = event.get("result", {})
                if isinstance(res, dict) and res.get("awaiting_user"):
                    q = res.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                    rounds.append(round_rec)
                    turn_record["status"] = "waiting_for_user"
                    turn_record["assistant_text"] = q
                    turn_record["rounds"] = rounds
                    turn_record["tool_events"] = all_tool_events
                    turn_record["ended_at"] = now_iso()
                    return turn_record

                non_clarify.append(event)

            rounds.append(round_rec)
            working_messages.append(tool_results_message(non_clarify))
        else:
            status = "max_tool_rounds"
            final_text = f"Dừng lại sau {max_tool_rounds} lượt công cụ."

        turn_record["status"] = status
        turn_record["assistant_text"] = final_text
        turn_record["rounds"] = rounds
        turn_record["tool_events"] = all_tool_events
        turn_record["ended_at"] = now_iso()
        return turn_record

    except Exception as exc:
        turn_record["status"] = "provider_error"
        turn_record["error"] = f"{type(exc).__name__}: {str(exc)}"
        turn_record["assistant_text"] = f"Lỗi Provider: {str(exc)}"
        turn_record["ended_at"] = now_iso()
        return turn_record


class HelpdeskUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/info":
            self.send_json(self.get_system_info())
            return

        if path == "/api/tools":
            self.send_json(self.get_tools_info())
            return

        if path == "/api/eval_cases":
            self.send_json(self.get_eval_cases())
            return

        if path == "/api/transcripts":
            self.send_json(self.list_transcripts())
            return

        if path.startswith("/api/transcripts/"):
            filename = path[len("/api/transcripts/"):]
            self.send_transcript(filename)
            return

        # Fallback to static files
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            body = self.read_json_body()
            if not body:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
                return
            
            user_text = body.get("message", "").strip()
            history = body.get("history", [])
            version = body.get("version", "v0")
            provider = body.get("provider", "openrouter")
            model = body.get("model") or None
            max_rounds = int(body.get("max_tool_rounds", 4))

            turn = run_chat_turn(
                user_text=user_text,
                history=history,
                version=version,
                provider_name=provider,
                model_override=model,
                max_tool_rounds=max_rounds,
            )

            # Metadata
            system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
            tools_path = ARTIFACTS_DIR / "tools.yaml"
            art_ver = build_artifact_version(version, system_prompt_path, tools_path)

            response_data = {
                "turn": turn,
                "artifact_version": artifact_version_dict(art_ver),
                "provider": provider,
                "model": model,
                "timestamp": now_iso(),
            }
            self.send_json(response_data)
            return

        if path == "/api/save_transcript":
            body = self.read_json_body()
            if not body:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
                return

            transcript_id = body.get("transcript_id") or f"web_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
            safe_id = safe_slug(transcript_id)
            save_path = TRANSCRIPTS_DIR / f"{safe_id}.transcript.json"
            save_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
            self.send_json({"status": "saved", "path": str(save_path), "filename": save_path.name})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def read_json_body(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def get_system_info(self) -> dict[str, Any]:
        system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"

        prompt_hash = file_hash(system_prompt_path) if system_prompt_path.exists() else "not_found"
        tools_hash = file_hash(tools_path) if tools_path.exists() else "not_found"
        v0 = build_artifact_version("v0", system_prompt_path, tools_path)

        providers_status = {
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "simulator": True,
        }

        default_provider = "simulator"
        for p in ["openrouter", "openai", "gemini", "anthropic"]:
            if providers_status.get(p):
                default_provider = p
                break

        return {
            "default_version": "v0",
            "artifact_version": v0.artifact_version,
            "prompt_hash": prompt_hash,
            "tools_hash": tools_hash,
            "providers_status": providers_status,
            "recommended_provider": default_provider,
            "tools_count": len(TOOL_FUNCTIONS),
            "system_prompt_preview": system_prompt_path.read_text(encoding="utf-8")[:600] if system_prompt_path.exists() else "",
        }

    def get_tools_info(self) -> dict[str, Any]:
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        if not tools_path.exists():
            return {"tools": []}
        return {"tools": load_tool_declarations(tools_path)}

    def get_eval_cases(self) -> dict[str, Any]:
        datasets = {}
        for fname in ["eval_base.json", "eval_adversarial.json", "eval_group.json", "eval_extension.json"]:
            fpath = DATA_DIR / fname
            if fpath.exists():
                try:
                    data = json.loads(fpath.read_text(encoding="utf-8"))
                    datasets[fname] = data.get("cases", [])
                except Exception:
                    pass
        return {"datasets": datasets}

    def list_transcripts(self) -> dict[str, Any]:
        results = []
        for path in sorted(SAMPLES_TRANSCRIPTS_DIR.glob("*.transcript.json")):
            results.append({"name": path.name, "category": "sample", "size": path.stat().st_size})
        for path in sorted(TRANSCRIPTS_DIR.glob("*.transcript.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            results.append({"name": path.name, "category": "saved", "size": path.stat().st_size})
        return {"transcripts": results}

    def send_transcript(self, filename: str) -> None:
        safe_name = Path(filename).name
        target = TRANSCRIPTS_DIR / safe_name
        if not target.exists():
            target = SAMPLES_TRANSCRIPTS_DIR / safe_name
        if not target.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Transcript file not found")
            return
        try:
            content = json.loads(target.read_text(encoding="utf-8"))
            self.send_json(content)
        except Exception as exc:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


def main() -> None:
    parser = argparse.ArgumentParser(description="Start IT Helpdesk Agent Interactive Web UI Server.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default 127.0.0.1)")
    args = parser.parse_args()

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server_address = (args.host, args.port)
    httpd = ThreadingHTTPServer(server_address, HelpdeskUIHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"\n=======================================================")
    print(f"🚀 IT Helpdesk Agent Web UI is running!")
    print(f"🌐 Open in browser: {url}")
    print(f"📁 Static Directory: {STATIC_DIR}")
    print(f"=======================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
