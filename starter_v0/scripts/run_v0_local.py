"""
run_v0_local.py — Local baseline simulation for VietTravel Tourism Helpdesk V0.

Does NOT require an API key. Uses keyword-based routing to simulate a weak V0
baseline. Produces a run JSON compatible with the run_eval.py schema, so the
same analysis tools can be applied.

Run:
    python scripts/run_v0_local.py --eval-cases data/eval_base_tourism.json --version v0
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RUNS_DIR = ROOT / "runs"

ALLOWED_CASE_FAILURE_TYPES = {
    "wrong_tool",
    "wrong_arg_value",
    "wrong_boundary",
    "unnecessary_tool",
    "out_of_scope",
    "missing_info",
}

# ── Keyword routers ───────────────────────────────────────────────────────────

BK_PATTERN = re.compile(r"\bBK-(\d+)\b", re.IGNORECASE)
CUST_PATTERN = re.compile(r"\bCUST-(\d+)\b", re.IGNORECASE)
HTL_PATTERN = re.compile(r"\bHTL-([A-Z0-9]+)\b", re.IGNORECASE)
PLAIN_NUMBER = re.compile(r"\b(1001|1002|1003|1004|1005|1006|1007|42|77|99|118|205|301)\b")


def _extract_booking_id(text: str) -> str | None:
    m = BK_PATTERN.search(text)
    if m:
        return f"BK-{m.group(1)}"
    return None


def _extract_customer_id(text: str) -> str | None:
    m = CUST_PATTERN.search(text)
    if m:
        return f"CUST-{m.group(1)}"
    return None


def _extract_hotel_id(text: str) -> str | None:
    m = HTL_PATTERN.search(text)
    if m:
        return f"HTL-{m.group(1).upper()}"
    return None


def _priority_from_text(text: str) -> str | None:
    t = text.lower()
    if "critical" in t:
        return "critical"
    if "high" in t or "cao" in t:
        return "high"
    if "medium" in t or "trung bình" in t or "tb" in t:
        return "medium"
    if "low" in t or "thấp" in t:
        return "low"
    return None


# ── Intent detection (intentionally weak — matches real V0 baseline) ───────────

class WeakBaselineRouter:
    """
    Simulates a V0 baseline with known weaknesses:

    1. Over-uses search_travel_kb for everything involving policy/questions.
    2. Does NOT ask clarify for missing IDs — guesses or returns generic answer.
    3. Does NOT enforce confirmation for create_support_ticket.
    4. Does NOT carry multi-turn context (treats each turn independently).
    5. Extracts booking_id from text but not always correctly.
    """

    def route(self, user_text: str, *, context: dict | None = None) -> list[dict[str, Any]]:
        text_lower = user_text.lower()
        calls: list[dict[str, Any]] = []

        # ── Out-of-scope detection ──────────────────────────────────────────
        out_scope_kw = ["viết code", "python", "sql", "api rest", "http request", "algorithm"]
        if any(kw in text_lower for kw in out_scope_kw):
            return []  # no tool (out_of_scope)

        # ── Meta / self-description ────────────────────────────────────────
        meta_kw = ["bạn là gì", "bạn có thể", "giúp được gì", "you are what", "what can you do"]
        if any(kw in text_lower for kw in meta_kw):
            return []  # no tool (answer_without_tool)

        # ── Booking ID present? ─────────────────────────────────────────────
        booking_id = _extract_booking_id(user_text)

        # ── Hotel ID present? ──────────────────────────────────────────────
        hotel_id = _extract_hotel_id(user_text)

        # ── Customer ID present? ───────────────────────────────────────────
        customer_id = _extract_customer_id(user_text)

        # ── Policy/SLA question? ────────────────────────────────────────────
        policy_kw = ["sla", "thời gian phản hồi", "chính sách", "độ ưu tiên", "refund", "hoàn tiền", "privacy", "bảo mật"]
        if any(kw in text_lower for kw in policy_kw):
            policy_area = "ticketing"
            if "privacy" in text_lower or "bảo mật" in text_lower or "dữ liệu" in text_lower:
                policy_area = "data_privacy"
            if hotel_id:
                calls.append({"name": "lookup_hotel", "args": {"hotel_id": hotel_id}})
            if booking_id:
                calls.append({"name": "check_booking_status", "args": {"booking_id": booking_id}})
            calls.append({"name": "travel_policy", "args": {"query": user_text, "policy_area": policy_area}})
            return calls

        # ── KB routing (visa/refund/payment/booking/insurance) ───────────────
        kb_kw = {
            "visa": ["visa", "nhập cảnh", "hộ chiếu"],
            "refund": ["hoàn tiền", "hủy", "cancel", "refund"],
            "payment": ["thanh toán", "mom", "zalo", "visa card", "trả góp", "installment"],
            "booking": ["đặt phòng", "hướng dẫn", "cách đặt", "làm sao đặt"],
            "insurance": ["bảo hiểm", "insurance"],
        }
        for cat, keywords in kb_kw.items():
            if any(kw in text_lower for kw in keywords):
                if booking_id:
                    calls.append({"name": "check_booking_status", "args": {"booking_id": booking_id}})
                calls.append({"name": "search_travel_kb", "args": {"query": user_text, "category": cat}})
                return calls

        # ── Hotel lookup ────────────────────────────────────────────────────
        if hotel_id:
            calls.append({"name": "lookup_hotel", "args": {"hotel_id": hotel_id}})

        # ── Customer lookup ─────────────────────────────────────────────────
        if customer_id:
            calls.append({"name": "lookup_customer", "args": {"customer_id": customer_id}})

        # ── Booking status (BK- present or 'trạng thái', 'tình trạng') ─────
        status_kw = ["trạng thái", "tình trạng", "đang ở", "booking", "trạng thái booking"]
        if booking_id and any(kw in text_lower for kw in status_kw):
            calls.append({"name": "check_booking_status", "args": {"booking_id": booking_id}})
            return calls

        # ── create_support_ticket (ISSUE: no confirmation enforcement!) ─────
        ticket_kw = ["tạo ticket", "tạo vé", "ticket", "phản hồi", "hỗ trợ", "lỗi", "sự cố"]
        if any(kw in text_lower for kw in ticket_kw):
            summary = user_text[:200]
            priority = _priority_from_text(user_text) or "medium"
            # V0 BUG: does NOT call clarify for confirmation — calls directly!
            calls.append({
                "name": "create_support_ticket",
                "args": {
                    "summary": summary,
                    "priority": priority,
                    "booking_id": booking_id or "",
                    "confirmed": False,  # V0 weakness: no confirmation step
                }
            })
            return calls

        # ── Missing ID without clarification (V0 weakness!) ─────────────────
        missing_id_kw = ["mã", "số", "booking", "khách hàng", "id"]
        if any(kw in text_lower for kw in missing_id_kw) and not (booking_id or customer_id or hotel_id):
            # V0 BUG: does NOT call clarify — just returns no tool call or generic
            # This simulates the missing_info failure mode
            if "tra cứu" in text_lower or "kiểm tra" in text_lower or "xem" in text_lower:
                # V0 makes no tool call when ID is missing
                return []
            calls.append({"name": "search_travel_kb", "args": {"query": user_text, "category": "all"}})
            return calls

        # ── Parallel calls (fallback: check multiple) ───────────────────────
        if booking_id and hotel_id:
            calls.append({"name": "check_booking_status", "args": {"booking_id": booking_id}})
            calls.append({"name": "lookup_hotel", "args": {"hotel_id": hotel_id}})
            return calls

        # ── Default: search KB ─────────────────────────────────────────────
        calls.append({"name": "search_travel_kb", "args": {"query": user_text, "category": "all"}})
        return calls


# ── Evaluation ────────────────────────────────────────────────────────────────

def compare_subset(expected: dict[str, Any], actual: dict[str, Any]) -> tuple[bool, list[str], int, int]:
    failures: list[str] = []
    total = 0
    correct = 0
    for key, expected_value in expected.items():
        total += 1
        actual_value = actual.get(key)
        if key == "missing_fields":
            expected_set = set(expected_value)
            actual_set = set(actual_value or [])
            ok = expected_set.issubset(actual_set)
        else:
            ok = str(expected_value).strip().lower() == str(actual_value or "").strip().lower()
        if ok:
            correct += 1
        else:
            failures.append(f"{key}: expected {expected_value!r}, got {actual_value!r}")
    return len(failures) == 0, failures, correct, total


def best_arg_match(expected_args: dict[str, Any], actual_calls: list[tuple[int, dict[str, Any]]]) -> tuple[int, list[str], int, int] | None:
    best: tuple[int, list[str], int, int] | None = None
    for index, actual_call in actual_calls:
        _, arg_failures, arg_correct, arg_total = compare_subset(expected_args, actual_call.get("args", {}))
        candidate = (index, arg_failures, arg_correct, arg_total)
        if best is None or (arg_correct, -len(arg_failures)) > (best[2], -len(best[1])):
            best = candidate
    return best


def evaluate_phase_b(case: dict[str, Any], tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
    expect = case["expect"]
    case_failure_type = case["failure_type"]

    if expect.get("no_tool"):
        passed = not tool_calls
        return {
            "passed": passed,
            "routing_correct": passed,
            "args_correct": passed,
            "actual_tool_calls": tool_calls,
            "actual_text": None,
            "case_failure_type": case_failure_type,
            "observed_mismatch": None if passed else "unexpected_tool_call",
            "failure_type": None if passed else case_failure_type,
            "failures": [] if passed else ["expected no tool call"],
        }

    expected_calls = expect.get("tool_calls", [])
    failures: list[str] = []
    routing_correct = True
    args_correct = True
    observed_mismatch: str | None = None
    unmatched_actual: dict[int, dict[str, Any]] = {index: call for index, call in enumerate(tool_calls)}

    for expected_call in expected_calls:
        same_name = [
            (index, actual_call)
            for index, actual_call in unmatched_actual.items()
            if actual_call["name"] == expected_call["name"]
        ]
        if not same_name:
            routing_correct = False
            args_correct = False
            observed_mismatch = observed_mismatch or "missing_tool_call"
            failures.append(f"missing tool call {expected_call['name']}")
            continue

        match = best_arg_match(expected_call.get("args", {}), same_name)
        if match is None:
            routing_correct = False
            args_correct = False
            observed_mismatch = observed_mismatch or "missing_tool_call"
            failures.append(f"missing tool call {expected_call['name']}")
            continue

        matched_index, arg_failures, arg_correct_count, arg_total = match
        unmatched_actual.pop(matched_index, None)
        if arg_correct_count != arg_total:
            args_correct = False
            observed_mismatch = observed_mismatch or "wrong_arg_value"
            failures.extend(arg_failures)

    for actual_call in unmatched_actual.values():
        routing_correct = False
        args_correct = False
        observed_mismatch = observed_mismatch or "extra_tool_call"
        failures.append(f"extra tool call {actual_call['name']}")

    passed = routing_correct and args_correct and not failures
    return {
        "passed": passed,
        "routing_correct": routing_correct,
        "args_correct": args_correct,
        "actual_tool_calls": tool_calls,
        "actual_text": None,
        "case_failure_type": case_failure_type,
        "observed_mismatch": None if passed else observed_mismatch,
        "failure_type": None if passed else case_failure_type,
        "failures": failures,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    measured = [item for item in results if item["result"].get("failure_type") != "provider_error"]
    provider_errors = total - len(measured)
    passed = sum(1 for item in measured if item["result"]["passed"])
    summary: dict[str, Any] = {
        "total_cases": total,
        "measured_cases": len(measured),
        "provider_error_cases": provider_errors,
        "passed_cases": passed,
        "case_accuracy": round(passed / len(measured), 4) if measured else 0.0,
    }
    phase_b = [item for item in measured if item["phase"] == "B"]
    if phase_b:
        routing = sum(1 for item in phase_b if item["result"].get("routing_correct"))
        args = sum(1 for item in phase_b if item["result"].get("args_correct"))
        summary.update({
            "tool_routing_accuracy": round(routing / len(phase_b), 4),
            "argument_accuracy": round(args / len(phase_b), 4),
        })
    failure_counts: dict[str, int] = {}
    observed_mismatch_counts: dict[str, int] = {}
    for item in measured:
        ft = item["result"].get("failure_type")
        if ft:
            failure_counts[ft] = failure_counts.get(ft, 0) + 1
        om = item["result"].get("observed_mismatch")
        if om:
            observed_mismatch_counts[om] = observed_mismatch_counts.get(om, 0) + 1
    summary["failure_counts"] = failure_counts
    summary["observed_mismatch_counts"] = observed_mismatch_counts
    return summary


def case_messages(case: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    if "turns" in case:
        turns = case["turns"]
        latest = turns[-1]["content"]
        previous = turns[:-1]
        previous_text = "\n".join(
            f"- Earlier turn {index + 1}: {item['content']}"
            for index, item in enumerate(previous)
        )
        return latest, [{"role": "user", "content": previous_text}]
    return case.get("input") or case.get("query", ""), []


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local V0 baseline for VietTravel Tourism Helpdesk.")
    parser.add_argument("--eval-cases", type=Path, default=DATA_DIR / "eval_base_tourism.json")
    parser.add_argument("--version", default="v0")
    parser.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    args = parser.parse_args()

    # Load cases
    data = json.loads(args.eval_cases.read_text(encoding="utf-8"))
    cases = [c for c in data["cases"] if c["phase"] == "B"]
    print(f"Loaded {len(cases)} cases from {args.eval_cases}")
    print(f"Router: WeakBaselineRouter (intentionally incomplete V0)")
    print("=" * 60)

    router = WeakBaselineRouter()
    results: list[dict[str, Any]] = []

    for case in cases:
        latest_text, _ = case_messages(case)
        calls = router.route(latest_text)
        result = evaluate_phase_b(case, calls)
        status = "PASS" if result["passed"] else "FAIL"
        failure = result.get("failure_type") or ""
        print(f"{case['id']:<30} {status:<5} {failure}")

        results.append({
            "id": case["id"],
            "phase": case["phase"],
            "suite": case.get("suite", "base"),
            "case_suite": case.get("suite", "base"),
            "is_multiturn": "turns" in case,
            "metadata": case.get("metadata", {}),
            "input": case.get("input") or case.get("query") or (case.get("turns") or [{}])[-1].get("content", ""),
            "expect": case["expect"],
            "result": result,
            "tool_results": [],  # no real tool execution in local mode
        })

    summary = summarize(results)
    print()
    for key, value in summary.items():
        print(f"{key}: {value}")

    # Save run
    args.runs_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    timestamp = now.strftime("%Y%m%dT%H%M%S%f")
    run_id = f"v0_local_{args.eval_cases.stem}_{timestamp}"
    payload = {
        "run_id": run_id,
        "version": args.version,
        "system_prompt": "artifacts/system_prompt.md (VietTravel Tourism Helpdesk — intentionally weak v0)",
        "tools": "artifacts/tools.yaml (7 tools: clarify, search_travel_kb, check_booking_status, lookup_customer, lookup_hotel, travel_policy, create_support_ticket)",
        "eval_cases": str(args.eval_cases),
        "dataset_id": data.get("dataset_id", ""),
        "dataset_role": data.get("dataset_role", ""),
        "generated_at": now.isoformat(timespec="seconds"),
        "provider": "local_baseline",
        "model": "WeakBaselineRouter (keyword-based, intentionally incomplete)",
        "phase": "B",
        "summary": summary,
        "results": results,
    }
    out_path = args.runs_dir / f"{run_id}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nSaved: {out_path}")
    print()
    print("=" * 60)
    print("TOP FAILURE ANALYSIS (for V1 hypothesis):")
    print("=" * 60)
    failure_counts = summary.get("failure_counts", {})
    mismatch_counts = summary.get("observed_mismatch_counts", {})
    for ftype, count in sorted(failure_counts.items(), key=lambda x: -x[1]):
        print(f"  {ftype}: {count} cases")
    print()
    print("Observed mismatch breakdown:")
    for om, count in sorted(mismatch_counts.items(), key=lambda x: -x[1]):
        print(f"  {om}: {count} cases")


if __name__ == "__main__":
    main()
