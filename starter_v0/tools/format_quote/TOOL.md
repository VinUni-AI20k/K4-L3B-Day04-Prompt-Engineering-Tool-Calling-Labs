---
name: format_quote
track: core
kind: local_formatter
provider: local_formatter
requires_env: []
inputs: [findings, template, quote_title]
outputs: [markdown, template, quote_title, total, finding_count]
side_effect: false
---
# format_quote

Formats already-collected findings into a brief, detailed, or invoice quote and
computes the total when findings carry a numeric `price`. It never fetches new
data; it only formats what the caller already has.
