from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


load_lab_env(ROOT)

SCENARIOS = [
    {
        "id": "demo_normal_service_status",
        "turns": ["Dịch vụ VPN production hiện có đang gặp sự cố không?"],
    },
    {
        "id": "demo_missing_info",
        "turns": ["Kiểm tra Wi-Fi trên laptop của mình giúp nhé."],
        "tool_choice": "required",
    },
    {
        "id": "demo_multiturn_cancel",
        "turns": [
            "Tạo ticket lỗi máy in cho máy PR-505 mức medium.",
            "Thôi hủy đi, không tạo ticket nữa.",
            "Thay vào đó, tìm hướng dẫn khắc phục lỗi máy in.",
        ],
    },
    {
        "id": "demo_ticket_confirmation",
        "turns": [
            "Tạo ticket mức high cho lỗi VPN trên LT-204 giúp mình.",
            "Tôi xác nhận tạo ticket: lỗi VPN trên LT-204, priority high.",
        ],
    },
]


def record_scenario(scenario: dict, *, args, provider, tools, system_prompt, artifact_version, model) -> Path:
    out_dir: Path = args.transcripts_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{scenario['id']}.transcript.json"
    transcript = {
        "transcript_id": scenario["id"],
        **artifact_version_dict(artifact_version),
        "provider": args.provider,
        "model": model,
        "system_prompt": str(args.system_prompt),
        "tools": str(args.tools),
        "history_window": args.history_window,
        "max_tool_rounds": args.max_tool_rounds,
        "ui": "record_demo_transcripts",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    history: list[dict[str, str]] = []
    for index, user_text in enumerate(scenario["turns"], start=1):
        print(f"  turn {index}: {user_text}", flush=True)
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, args.history_window),
            {"role": "user", "content": user_text},
        ]
        turn = {
            "turn_index": index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=tools,
            model=model,
            max_tool_rounds=args.max_tool_rounds,
            verbose=True,
            tool_choice=scenario.get("tool_choice"),
        )
        turn.update(result)
        turn["ended_at"] = now_iso()
        transcript["turns"].append(turn)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": result.get("assistant_text") or ""})
        print(f"    status={turn.get('status')} tools={[e.get('tool') for e in turn.get('tool_events') or []]}", flush=True)
    write_transcript(path, transcript)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the four required demo transcripts.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], default="openrouter")
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="v3")
    parser.add_argument("--system-prompt", type=Path, default=ROOT / "artifacts" / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()

    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(args.tools))
    provider = make_provider(args.provider)
    model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)

    written = []
    for scenario in SCENARIOS:
        print(f"Recording {scenario['id']}...", flush=True)
        path = record_scenario(
            scenario,
            args=args,
            provider=provider,
            tools=tools,
            system_prompt=system_prompt,
            artifact_version=artifact_version,
            model=model,
        )
        written.append(str(path))
    print(json.dumps({"ok": True, "files": written}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
