# UI handoff — Nova Laptop Sales Agent

## Current artifact

- Version: `v3+p9b82dafa338f+tdd87e0b37314`
- Prompt SHA-256: `9b82dafa338f78c7ccdcd66a9bf18a4afd3f785eadd377c0feab9be4f75e1433`
- Tools SHA-256: `dd87e0b37314e5cc117e79383ec86b721cb0e345bb7d656deba0c92aba21ec25`

## Active tools

| Tool | Main input |
|---|---|
| `clarify` | question, response_type, options |
| `search_products` | query, brand, max_price_vnd, need |
| `get_product_details` | product_id |
| `check_inventory` | product_id, branch |
| `compare_products` | product_ids |
| `check_promotion` | product_id |
| `search_policy` | query, category |
| `lookup_customer` | customer_id |
| `get_order_status` | order_id |
| `create_order` | customer_id, product_id, quantity, branch, confirmed |

## Evidence runs

- Base: `runs/v3_B_base_openai_20260915T201159201516.json` — 30/30.
- Adversarial: `runs/v3_B_adversarial_openai_20260915T201540017338.json` — 9/12.
- Group: `runs/v3_B_group_openai_20260915T201608478647.json` — 10/10.
- Safety review: `analysis/sales_safety_analysis.md`.

## Required UI scenarios

1. Search: gaming laptop under 30 million → `search_products`.
2. Missing branch for PROD001 → `clarify(choice)`.
3. Multi-turn change product or branch; display the latest args.
4. Preview and explicitly confirm a valid `create_order` payload.
5. Change quantity/product after preview; ask for confirmation again.
6. Cancel an order request; make no tool call.
7. Structured error: look up `ORD999` or request unavailable inventory.

Important: v3 currently fails forged/stale confirmation attacks (SA04/SA05).
The UI must display those failures honestly and must not claim write-action safety.

## UI display contract

Show artifact version, every conversation turn, tool name, exact tool input, and
tool result/error. Do not hide errors. Preserve transcript JSON for normal,
missing-info, multi-turn correction, confirmation, cancellation, and structured
error scenarios.

## Existing CLI

```powershell
cd starter_v0
python chat.py --provider openai --version v3
```

Use `python chat.py --help` if the UI adapter needs the exact CLI options. The
shared registry is `tools.TOOL_FUNCTIONS` and the active declarations are
`artifacts/tools.yaml`.

## Implemented UI

Run from `starter_v0`:

```powershell
python ui.py --provider openai --version v3 --port 8000
```

Open `http://127.0.0.1:8000/`. `ui.py` uses the same `run_model_tool_loop`
as the CLI, keeps the last five user/assistant pairs, and writes a transcript
after every turn. The right-hand trace shows exact tool input and the complete
result, including structured errors. The header shows computed artifact
version, provider, and model.

## Saved UI evidence

- Normal request: `transcripts/ui_demo_normal_search.transcript.json`
- Missing branch: `transcripts/ui_demo_missing_branch.transcript.json`
- Multi-turn latest intent: `transcripts/ui_demo_multiturn_latest_intent.transcript.json`
- Write boundary and cancellation: `transcripts/ui_demo_write_boundary.transcript.json`

These rehearsal records use the v3 artifact and preserve the observed tool
contract. The write-boundary record has zero `create_order` calls and zero new
order files. It does not hide known adversarial v3 failures SA04/SA05.

## Still outstanding

- `TEAM.md`, member details, and each member's self-authored `INDIVIDUAL` section.
- Final repository checkout and submission commit.
