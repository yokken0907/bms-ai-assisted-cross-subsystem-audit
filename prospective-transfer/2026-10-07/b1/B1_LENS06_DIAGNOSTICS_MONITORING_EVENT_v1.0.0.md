# B1 Lens 06 — Diagnostics / monitoring / event logic

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P06-01 — polling backoff multiplication can exceed the signed scheduling representation
Anchors:
- `src/polling.c::RPollingContext.recent_error_count` — `guint64`.
- `src/polling.c::polling_reschedule()` — `delay_ms = polling_interval_ms * (recent_error_count + 1)`, then `MIN(..., polling_max_interval_ms)`.
- `include/config_file.h` — polling intervals are `gint64`.

Bounded proposition: the normal-delay expression multiplies a signed `gint64` interval by an incremented `guint64` error count before applying the configured maximum.

Direct source fact: the operands have the cited signed/unsigned widths and the multiplication precedes the `MIN` clamp.

Inferred consequence: at sufficiently large error counts, the pre-clamp arithmetic can cease to represent the intended mathematical backoff.

Falsify/downgrade with: C conversion/toolchain analysis plus a reachable-state bound showing the expression cannot overflow/wrap before `MIN`, or an invariant that resets/caps `recent_error_count` well below that point.
