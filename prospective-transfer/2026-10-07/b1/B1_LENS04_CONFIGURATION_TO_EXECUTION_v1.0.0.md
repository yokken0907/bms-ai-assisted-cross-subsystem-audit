# B1 Lens 04 — Configuration-to-execution wiring

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P04-01 — polling interval seconds are multiplied in `gint` before storage in `gint64`
Anchors:
- `src/config_file.c::parse_polling_section()`.
- `include/config_file.h::RaucConfig.polling_interval_ms/polling_max_interval_ms`.
- `src/polling.c::polling_reschedule()`.

Bounded proposition: accepted positive `gint` polling intervals are converted to milliseconds using `interval_sec * 1000` / `max_interval_sec * 1000` before assignment to `gint64`, and the default maximum also uses `interval_sec * 4`.

Direct source fact: `interval_sec` and `max_interval_sec` are `gint`; no upper bound other than the type range is checked; the multiplications occur on those `gint` operands.

Inferred consequence: sufficiently large accepted second values can cross the representable range of the intermediate signed-int arithmetic before the widened assignment, altering configured scheduling values.

Falsify/downgrade with: a C/toolchain contract or upstream bound proving the intermediate operations cannot overflow for accepted configuration values.

### P04-02 — binary-suffixed configuration parser does not validate the full token
Anchors:
- `src/utils.c::key_file_consume_binary_suffixed_string()`.
- consumers in `src/config_file.c` including event-log max-size, slot region-start/region-size, and boot-eMMC size-limit.
- `docs/reference.rst` describes optional single K/M/G/T binary suffixes for region values.

Bounded proposition: the helper parses a decimal prefix, inspects only the first non-digit character for a scale, and returns without checking that the token ends there or that the left shift preserves the numeric value.

Direct source fact: `g_ascii_strtoull(string, &scale, 10)` is followed by a switch on `*scale` and `return result << scale_shift`; no end-of-string or overflow check follows.

Inferred consequence: malformed trailing text can be accepted, and sufficiently large scaled values can wrap during the shift.

Falsify/downgrade with: an upstream tokenizer/validator proving every call receives only a canonical in-range decimal plus optional one-character suffix.
