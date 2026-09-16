"""Live verification for bonus tool: software_catalog with OpenRouter LLM."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop

load_lab_env(ROOT)

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_decls = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_decls)

provider = make_provider("openrouter")

test_prompts = [
    "Cho mình hỏi phần mềm Docker Desktop công ty có cho phép dùng không, có cần bản quyền không và cài đặt thế nào?",
    "Mình có được phép cài BitTorrent trên laptop công ty để tải tài liệu không?",
]

for idx, user_prompt in enumerate(test_prompts, start=1):
    print(f"\n============================================================")
    print(f"TEST CASE {idx}")
    print(f"User: {user_prompt}")
    print(f"============================================================")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    result = run_model_tool_loop(
        provider=provider,
        messages=messages,
        tools=openai_tools,
        model=None,
        max_tool_rounds=3,
    )
    print("\n--- FINAL ASSISTANT RESPONSE ---")
    print(result["assistant_text"])
