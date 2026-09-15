# Part A audit — inherited Sales v0-v3 evidence

## Verification scope

- Canonical dataset: `data/sales/eval_sales_base.json`
- Provider/model: OpenAI / `gpt-4o-mini`
- Case count: 30 for every inherited run
- Current prompt SHA-256: `9b82dafa338f78c7ccdcd66a9bf18a4afd3f785eadd377c0feab9be4f75e1433`
- Current tools SHA-256: `dd87e0b37314e5cc117e79383ec86b721cb0e345bb7d656deba0c92aba21ec25`

## Run audit

| Version | Run path | Cases | Measured | Provider errors | Accuracy | Prompt hash | Tools hash | Matches version log | Status |
|---|---|---:|---:|---:|---:|---|---|---|---|
| v0 | `runs/v0_B_base_openai_20260915T192838096502.json` | 30 | 30 | 0 | 0.8333 | `2fef25f256348aed0baf9ce959c6b698f4424a8d5aa982267a078bb381876e34` | `1f59ff7dd2118277e255ad4e2626052fc461102746da01b8a05e9abb081a6ade` | Yes | VERIFIED |
| v1 | `runs/v1_B_base_openai_20260915T193300682162.json` | 30 | 30 | 0 | 0.9000 | `2fef25f256348aed0baf9ce959c6b698f4424a8d5aa982267a078bb381876e34` | `dd87e0b37314e5cc117e79383ec86b721cb0e345bb7d656deba0c92aba21ec25` | Yes | VERIFIED |
| v2 | `runs/v2_B_base_openai_20260915T193603285842.json` | 30 | 30 | 0 | 1.0000 | `9ec08a7ccaefd6d4dd4ad1361ec8485368915b726eddd16f3f6dae621181ac52` | `dd87e0b37314e5cc117e79383ec86b721cb0e345bb7d656deba0c92aba21ec25` | Yes | VERIFIED |
| v3 | `runs/v3_B_base_openai_20260915T201159201516.json` | 30 | 30 | 0 | 1.0000 | `9b82dafa338f78c7ccdcd66a9bf18a4afd3f785eadd377c0feab9be4f75e1433` | `dd87e0b37314e5cc117e79383ec86b721cb0e345bb7d656deba0c92aba21ec25` | Yes | VERIFIED WITH NEW V3 RUN |

## Consistency checks

- All four runs point to `data/sales/eval_sales_base.json`; no fixed case content was changed between versions.
- All four runs use OpenAI `gpt-4o-mini` and 30 cases.
- Every run has `measured_cases == 30` and `provider_error_cases == 0`.
- Every run path exists and its accuracy/hash fields match `artifacts/version_log.csv`.
- v0 is the baseline; v1, v2, and v3 each have a distinct artifact change and hypothesis in the version log.
- The merge conflict in the active artifacts was resolved within the existing v3 content. The current `system_prompt.md` and `tools.yaml` hashes match the verified v3 run.
- The fresh v3 verification remained `30/30`, `0` provider errors, and `1.0000` accuracy. No old run was deleted or rewritten.

## Part A conclusion

**VERIFIED WITH NEW V3 RUN**

