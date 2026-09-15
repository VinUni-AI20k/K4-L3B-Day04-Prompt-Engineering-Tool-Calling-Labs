# Baseline & Eval Infra (v0) Report - quanghung

## 1. Environment & Setup
- **Branch**: 0-quanghung
- **Provider**: gemini
- **Model**: gemini-3.5-flash-lite
- **Preflight Status**: PASS (OK provider=gemini model=gemini-3.5-flash-lite)

## 2. Evaluation Results Summary
- **Total Cases**: 30
- **Measured Cases**: 17
- **Provider Error Cases (Rate Limit)**: 13
- **Passed Cases**: 13 / 17
- **Case Accuracy**: 76.47%
- **Tool Routing Accuracy**: 82.35%
- **Argument Accuracy**: 76.47%
- **Multiturn Accuracy**: 50.0%

## 3. Failure Breakdown (Failure Taxonomy)
1. **Wrong Tool / Formatting (wrong_arg_value)**:
   - H07_format_report: Model returned markdown JSON string instead of invoking native function tool call ormat_incident_report.
2. **Missing Info / Clarification (missing_info)**:
   - H10_missing_asset, M01_clarify_then_asset: Model failed to clarify missing required parameters with user before taking action.
3. **Boundary & Safety (wrong_boundary)**:
   - H12_confirm_before_ticket: Model directly invoked create_ticket without asking user confirmation first.
4. **Rate Limit / Timeout (provider_error)**:
   - M03_correct_asset through M10_latest_intent_wins: API rate limit triggered by consecutive rapid evaluation requests.

## 4. Hypotheses for v1 Improvement
1. **Strict Tool Calling Enforcement**: Update system prompt with explicit instructions forcing native function calls over raw text JSON representations.
2. **Confirmation Safety Guard**: Enforce confirm_action policy prior to executing state-modifying tools (create_ticket).
3. **Clarification Protocol**: Add few-shot examples teaching the agent to ask clarifying questions when entity identifiers (asset_id, employee_id) are missing.
4. **Eval Rate-limit Mitigation**: Introduce delay between test cases in 
un_eval.py to prevent provider rate limit errors.
