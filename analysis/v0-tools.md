# TV3 — Tool/Input Error Analysis (Huy)

This analysis is based on the source code and local checks. There is no actual v0 run yet, so prompt-related risks have not been confirmed with model results.

## Verified Issues

| Issue | Evidence | Fix |
|---|---|---|
| Evaluation reports PASS even when a tool crashes | Adding an `unexpected` argument to `inspect_device` causes a `TypeError`, but the evaluator still reports PASS | Validate the schema before calling a tool; evaluate `tool_results`, not only expected tool names and arguments |
| Invalid or missing input | `environment="demo"` returns `not_found`; a missing `asset_id` returns `asset_not_found` | Call `clarify` when the asset ID or environment is missing or unclear; never guess values |
| Tool cannot run without configuration | Without an API key, `search_device_info` returns `missing_api_key` | Configure `TAVILY_API_KEY` when web search is used; report this as a configuration error, not a tool-routing error |

## Areas to Improve

| Issue | Fix |
|---|---|
| Tool descriptions are unclear | State clearly: `check_service_status` checks service availability; `search_kb` finds instructions; `inspect_device` checks a specific device |
| The prompt has no clear rule for corrections and cancellation | Prioritize the newest request; replace corrected IDs; stop an action that the user cancels |
| Ticket confirmation relies only on `confirmed` | Bind confirmation to the current summary, priority, and asset; ask again if any ticket detail changes |
| The agent does not return tool results to the model in the same run | Add a result-processing loop for dependent tool calls and a final response based on tool evidence |

**Definitions:** A wrong-tool error means selecting the wrong action. A wrong-input error means missing or incorrect arguments. An execution error means the tool cannot complete because of configuration or code. `needs_confirmation` is a correct safety block, not a tool error.