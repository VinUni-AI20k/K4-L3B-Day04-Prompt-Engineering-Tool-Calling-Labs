"""Person 3 only: run the unchanged adversarial evaluator through Groq compatibility.
Usage: .venv\\Scripts\\python.exe -B scripts/run_safety_groq.py --model openai/gpt-oss-120b
GROQ_API_KEY stays in local .env. No provider/evaluator files are modified.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from env_loader import load_lab_env


def snapshot():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "tickets").glob("*.json"))}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-output-tokens", type=int, default=512)
    parser.add_argument("--request-interval", type=float, default=8.0)
    args=parser.parse_args()
    load_lab_env(ROOT)
    key=os.getenv("GROQ_API_KEY")
    model=args.model or os.getenv("GROQ_MODEL")
    if not key or not model:
        raise SystemExit("Configure GROQ_API_KEY locally and supply --model or GROQ_MODEL.")
    import run_eval
    from agent import HelpdeskAgent

    # Existing adapter targets the Groq endpoint, not OpenRouter infrastructure.
    os.environ["OPENROUTER_API_KEY"]=key
    os.environ["OPENROUTER_BASE_URL"]="https://api.groq.com/openai/v1"
    observations=[]
    class ObservedAgent(HelpdeskAgent):
        def run(self, *positional, **keywords):
            before=snapshot()
            try:
                return super().run(*positional, **keywords)
            finally:
                after=snapshot()
                observations.append({"before":before,"after":after,
                                     "created":sorted(after.keys()-before.keys()),
                                     "changed":sorted(k for k in before.keys() & after.keys() if before[k]!=after[k]),
                                     "removed":sorted(before.keys()-after.keys())})
    run_eval.HelpdeskAgent=ObservedAgent
    from openai.resources.chat.completions import Completions
    original_create = Completions.create
    provider_responses = []
    last_request = [None]
    def bounded_create(client, *positional, **keywords):
        if last_request[0] is not None:
            delay = args.request_interval - (time.monotonic() - last_request[0])
            if delay > 0:
                time.sleep(delay)
        last_request[0] = time.monotonic()
        keywords["max_tokens"] = args.max_output_tokens
        response = original_create(client, *positional, **keywords)
        provider_responses.append({
            "finish_reasons": [c.finish_reason for c in response.choices],
            "usage": response.usage.model_dump() if response.usage else None,
        })
        return response
    with patch.object(Completions, "create", bounded_create), tempfile.TemporaryDirectory(prefix="person3-adversarial-") as temporary:
        sys.argv=["run_eval.py","--provider","openrouter","--version","v3",
                  "--suite","adversarial","--eval-cases",str(ROOT/"data/eval_adversarial.json"),
                  "--model",model,"--runs-dir",temporary]
        run_eval.main()
        raw_path=next(Path(temporary).glob("*.json"))
        raw=raw_path.read_bytes()
        payload=json.loads(raw)
        redactions=[]
        # Fixed fixtures contain a synthetic password. Preserve grading, redact only saved text.
        def redact(value,path=""):
            if isinstance(value,dict):
                return {k:redact(v,path+"/"+k) for k,v in value.items()}
            if isinstance(value,list):
                return [redact(v,path+"/"+str(i)) for i,v in enumerate(value)]
            if isinstance(value,str):
                clean=value.replace(key,"[REDACTED_API_KEY]")
                clean=re.sub(r"\borg_[a-zA-Z0-9_-]+\b", "[REDACTED_ORG_ID]", clean)
                clean=re.sub(r"(?i)(password\s*[:=]\s*)[^\s\"\\]+",
                             r"\1[REDACTED_SYNTHETIC_SECRET]",clean)
                if clean!=value:
                    redactions.append(path)
                return clean
            return value
        payload=redact(payload)
        payload["actual_provider"]="groq"
        payload["provider_adapter"]="openrouter"
        payload["endpoint"]="https://api.groq.com/openai/v1"
        payload["safety_evidence"]={
            "max_output_tokens": args.max_output_tokens,
            "request_interval_seconds": args.request_interval,
            "provider_responses": provider_responses,
            "raw_sha256":hashlib.sha256(raw).hexdigest(),
            "redacted_json_paths":redactions,
            "note":"Only text redaction and provenance added; tool call names and evaluation metrics unchanged.",
            "case_filesystem":{r["id"]:obs for r,obs in zip(payload["results"],observations)},
            "implementation_sha256":{
                str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [ROOT/"agent.py",ROOT/"chat.py",ROOT/"tools/_shared.py",
                          ROOT/"tools/create_ticket/tool.py",ROOT/"tools/search_device_info/tool.py",
                          ROOT/"tools/search_device_info/public_products.json",
                          ROOT/"tools/search_kb/tool.py",ROOT/"tools/policy/tool.py",
                          ROOT/"data/eval_adversarial.json",ROOT/"run_eval.py"]
            },
        }
        destination=ROOT/"analysis/safety"
        destination.mkdir(parents=True,exist_ok=True)
        out=destination/raw_path.name
        out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("Reviewed evidence:",out)
        print("Actual provider: groq; compatibility adapter label: openrouter")
        print("Ticket files before/after each case:",[(r["id"],len(obs["before"]),len(obs["after"]))
              for r,obs in zip(payload["results"],observations)])


if __name__=="__main__":
    main()
