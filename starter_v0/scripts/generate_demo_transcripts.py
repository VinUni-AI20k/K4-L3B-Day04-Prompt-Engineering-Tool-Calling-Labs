from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import (
    now_iso,
    trim_history,
    run_model_tool_loop,
    write_transcript,
)

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def run_scenario(
    name: str,
    turns: list[str],
    provider_name: str = "openrouter",
    version_label: str = "v3",
) -> Path:
    print(f"\n=======================================================")
    print(f"🎬 Executing Live Scenario: {name}")
    print(f"=======================================================")
    
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    model = getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_PATH)

    transcript_id = f"{name}_{version_label}"
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"

    transcript = {
        "transcript_id": transcript_id,
        "scenario_name": name,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    history: list[dict[str, str]] = []

    for turn_idx, user_text in enumerate(turns, start=1):
        print(f"\n[Turn {turn_idx}] User: {user_text}")
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(history, window=5),
            {"role": "user", "content": user_text},
        ]

        turn_record = {
            "turn_index": turn_idx,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model,
                max_tool_rounds=4,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            print(f"[Turn {turn_idx}] Assistant: {assistant_text[:120]}...")
            for ev in result.get("tool_events", []):
                print(f"  -> Tool: {ev['tool']} | Args: {ev['args']}")
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })
            print(f"[Turn {turn_idx}] ERROR: {exc}")

        turn_record["ended_at"] = now_iso()
        transcript["turns"].append(turn_record)

    write_transcript(transcript_path, transcript)
    print(f"\n✅ Transcript saved: {transcript_path}")
    return transcript_path


def main():
    # 1. Yêu cầu bình thường
    run_scenario(
        name="scenario_1_normal_query",
        turns=[
            "Kiểm tra trạng thái dịch vụ VPN trên môi trường production giúp mình."
        ]
    )

    # 2. Thiếu thông tin và hỏi lại
    run_scenario(
        name="scenario_2_missing_info_clarify",
        turns=[
            "Máy tính của mình không vào được mạng, kiểm tra giúp mình với."
        ]
    )

    # 3. Hội thoại nhiều lượt có sửa/hủy
    run_scenario(
        name="scenario_3_multiturn_correct",
        turns=[
            "Kiểm tra kết nối của máy LT-204.",
            "À nhầm, kiểm tra máy LT-240 giúp mình."
        ]
    )

    # 4. Tạo ticket sau xác nhận
    run_scenario(
        name="scenario_4_ticket_confirmation",
        turns=[
            "Tạo ticket mức high cho lỗi VPN trên máy LT-204 giúp mình.",
            "Tôi xác nhận summary 'Lỗi VPN trên máy LT-204' và mức priority high. Hãy tạo ticket đi."
        ]
    )

    # 5. Bonus: Tra cứu bảo hành & vòng đời (check_asset_warranty)
    run_scenario(
        name="scenario_5_bonus_warranty",
        turns=[
            "Kiểm tra thời hạn bảo hành và tình trạng vòng đời của máy LT-204."
        ]
    )


if __name__ == "__main__":
    main()
