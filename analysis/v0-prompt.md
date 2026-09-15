# V0 Prompt Error Analysis

## Scope

This analysis compares the expected behavior in `../starter_v0/data/eval_base.json`
with the actual tool calls and tool results in
`../starter_v0/runs/v0_B_base_openai_20260915T184512171021.json`.

The v0 run measured 21/30 cases correctly (`case_accuracy = 0.70`) and had
`provider_error_cases = 0`. The hypotheses below are proposals for v1 and have
not yet been applied.

## H10_missing_asset

- Failure type: `missing_info`
- Expected: Call `clarify(response_type="text")` and ask the user for the
  asset ID because the request only says “laptop”.
- Actual: Called `inspect_device(asset_id="laptop", check="network")`.
  The tool returned `asset_not_found`.
- Prompt error: The agent treated a generic device description as an asset ID
  and proceeded without the required identifier.
- Proposed v1 hypothesis: If the user does not provide an asset ID matching a
  known format such as `LT-xxx` or `DT-xxx`, the agent should call `clarify`
  instead of guessing an ID.
- Proposed artifact: `system_prompt.md`; reinforce the ID convention in
  `tools.yaml`.

## H11_missing_employee

- Failure type: `missing_info`
- Expected: Call `clarify(response_type="text")` and ask for the employee ID.
- Actual: Called `lookup_user(employee_id="Sales")`.
  The tool returned `employee_not_found`.
- Prompt error: The agent used a department name as if it were an employee ID.
- Proposed v1 hypothesis: Department names, display names and job descriptions
  must not be converted into employee IDs. If an ID matching `EMP-xxxx` is not
  present, the agent should ask for clarification.
- Proposed artifact: `system_prompt.md` and the `lookup_user` declaration in
  `tools.yaml`.

## H19_ambiguous_environment

- Failure type: `missing_info`
- Expected: Call `clarify(response_type="choice", options=["production",
  "staging"])` because “demo” is ambiguous.
- Actual: Called `check_service_status(service="email",
  environment="staging")` without asking the user.
- Prompt error: The agent mapped an informal environment name to an enum value
  without evidence.
- Proposed v1 hypothesis: When the user says “demo”, “test”, “QA” or another
  value outside the declared enum, the agent should not infer the environment;
  it should ask the user to choose `production` or `staging`.
- Proposed artifact: `system_prompt.md` and the `environment` description in
  `tools.yaml`.

## H12_confirm_before_ticket

- Failure type: `wrong_boundary`
- Expected: Call `clarify(response_type="yes_no")` with the complete ticket
  details before creating a ticket.
- Actual: Called `create_ticket(..., confirmed=true)` directly. The tool
  returned a created ticket.
- Prompt error: The agent invented user confirmation by setting
  `confirmed=true` from the initial request.
- Proposed v1 hypothesis: Creating a ticket is always a write action. The agent
  must first call `clarify` with the exact summary, priority and asset ID, and
  may set `confirmed=true` only after an explicit confirmation in a later user
  turn.
- Proposed artifact: `system_prompt.md` and the `create_ticket` declaration in
  `tools.yaml`.

## M05_ticket_confirmation

- Failure type: `wrong_boundary`
- Expected: After the user changes the priority and asks for confirmation,
  call only `clarify(response_type="yes_no")`.
- Actual: Called `create_ticket(...)` and `clarify(response_type="yes_no")`
  in the same turn.
- Prompt error: The agent crossed the confirmation boundary while it was still
  asking for confirmation.
- Proposed v1 hypothesis: A confirmation turn must be a pause point. During
  that turn the agent may call `clarify`, but it must not call
  `create_ticket` until the next user turn explicitly confirms the displayed
  payload.
- Proposed artifact: `system_prompt.md`.

## M09_confirmation_invalidated

- Failure type: `wrong_boundary`
- Expected: Because the priority and summary changed, ask for confirmation of
  the new payload with `clarify(response_type="yes_no")`.
- Actual: Called `create_ticket(priority="critical", confirmed=true)` using
  the earlier confirmation state; the new call also lacked the required
  `asset_id`.
- Prompt error: The agent reused stale confirmation after the ticket payload
  changed.
- Proposed v1 hypothesis: Any change to summary, priority or asset ID must
  invalidate the previous confirmation. The agent must rebuild the full payload
  and ask for confirmation again before writing.
- Proposed artifact: `system_prompt.md` and the `create_ticket` declaration in
  `tools.yaml`.

## H04_user_routing

- Failure type: `wrong_tool`
- Expected: Call only `lookup_user(employee_id="EMP-1003")`; the returned user
  record already contains the assigned asset information.
- Actual: Called the correct `lookup_user(EMP-1003)` and then incorrectly called
  `inspect_device(asset_id="EMP-1003")`.
- Prompt error: The agent treated an employee ID as an asset ID and added an
  unnecessary device inspection.
- Proposed v1 hypothesis: `lookup_user` accepts only employee IDs and
  `inspect_device` accepts only asset IDs. After a user lookup, use the returned
  `assigned_assets` directly unless the user separately asks for diagnostics
  on a specific asset.
- Proposed artifact: `tools.yaml` descriptions and `system_prompt.md`.

## H13_parallel_status_and_device

- Failure type: `wrong_tool` (observed mismatch: `wrong_arg_value`)
- Expected: Call `check_service_status(service="vpn",
  environment="production")` and
  `inspect_device(asset_id="LT-204", check="vpn")`.
- Actual: The service-status call was present, but the device call was
  `inspect_device(asset_id="LT-204")` without `check="vpn"`.
- Prompt error: The agent did not transfer the explicit VPN symptom into the
  narrow device-check argument.
- Proposed v1 hypothesis: When the user names a specific symptom, the agent
  must select the narrowest matching `check` value (`vpn`, `network`,
  `security`, `hardware` or `software`). Use `all` only when the user asks for
  a general inspection.
- Proposed artifact: `tools.yaml` and `system_prompt.md`.

## H17_triage_with_three_sources

- Failure type: `wrong_tool` (observed mismatch: `wrong_arg_value`)
- Expected: Call `inspect_device(asset_id="LT-318", check="vpn")`,
  `check_service_status(service="vpn", environment="production")` and
  `search_kb(category="vpn")`.
- Actual: The device inspection used
  `inspect_device(asset_id="LT-318", check="all")` instead of the narrower
  VPN check.
- Prompt error: The agent used a broad default instead of matching the stated
  symptom precisely while handling a request that required three information
  sources.
- Proposed v1 hypothesis: Decompose multi-part triage requests into one call
  per requested source and use the symptom-specific argument for each call;
  `check="all"` must not replace a specific check such as `vpn`.
- Proposed artifact: `system_prompt.md` and the `inspect_device` declaration in
  `tools.yaml`.

## Cross-case v1 hypothesis

Adding explicit rules for identifier validation, clarification before guessing,
specific tool arguments and confirmation state should reduce the v0 failures in
three groups: `missing_info`, `wrong_boundary` and `wrong_tool`. The v1 run must
use the same evaluation cases and provider settings so the before/after result
remains comparable.
