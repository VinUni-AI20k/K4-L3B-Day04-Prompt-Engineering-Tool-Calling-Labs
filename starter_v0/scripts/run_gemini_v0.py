"""
run_gemini_v0.py — Helper: Run V0 evaluation with Google Gemini.

Prerequisites (set BEFORE running this script):
    $env:GEMINI_API_KEY = "AIza..."

Usage:
    python scripts/run_gemini_v0.py
    python scripts/run_gemini_v0.py --suite base
    python scripts/run_gemini_v0.py --suite adversarial
    python scripts/run_gemini_v0.py --suite group
    python scripts/run_gemini_v0.py --model gemini-2.5-pro
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _has_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def _run_preflight(model: str | None) -> bool:
    """Return True if preflight succeeds (provider can make one tool call)."""
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "preflight_provider.py"),
        "--provider", "gemini",
    ]
    if model:
        cmd.extend(["--model", model])
    print("[1/3] Preflight: gọi thử 1 tool call để xác nhận key + model hoạt động...")
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return False
    print(proc.stdout.strip())
    return True


def _run_eval(suite: str, model: str | None) -> int:
    suite_to_cases = {
        "base": "data/eval_base_tourism.json",
        "adversarial": "data/eval_adversarial_tourism.json",
        "group": "data/eval_group.json",
    }
    if suite not in suite_to_cases:
        raise SystemExit(f"Unknown suite: {suite}. Use base | adversarial | group.")
    cmd = [
        sys.executable,
        str(ROOT / "run_eval.py"),
        "--provider", "gemini",
        "--version", "v0",
        "--phase", "B",
        "--suite", suite,
        "--eval-cases", str(ROOT / suite_to_cases[suite]),
    ]
    if model:
        cmd.extend(["--model", model])
    print(f"\n[2/3] Run eval: suite={suite}, eval_cases={suite_to_cases[suite]}, model={model or 'default'}")
    print(" ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return proc.returncode


def _print_summary_hint() -> None:
    print("\n[3/3] Sau khi run xong, mở file JSON mới nhất trong runs/ để xem summary.")
    runs_dir = ROOT / "runs"
    if runs_dir.exists():
        files = sorted(runs_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
        for f in files:
            print(f"  - {f.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run V0 evaluation with Google Gemini.")
    parser.add_argument("--suite", choices=["base", "adversarial", "group"], default="base")
    parser.add_argument("--model", default=None, help="Model override (default: gemini-2.5-flash)")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    if not _has_key():
        raise SystemExit(
            "GEMINI_API_KEY chưa được set. Trước khi chạy, gõ:\n"
            "    $env:GEMINI_API_KEY = \"AIza...\"\n"
            "(Lấy key miễn phí tại https://aistudio.google.com/apikey)"
        )

    if not args.skip_preflight:
        if not _run_preflight(args.model):
            raise SystemExit("Preflight thất bại — kiểm tra key hoặc tên model.")

    rc = _run_eval(args.suite, args.model)
    if rc != 0:
        raise SystemExit(f"Eval exited with code {rc}.")
    _print_summary_hint()


if __name__ == "__main__":
    main()
