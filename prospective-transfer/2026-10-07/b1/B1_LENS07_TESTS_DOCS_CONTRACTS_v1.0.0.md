# B1 Lens 07 — Contemporaneous tests/docs/contracts versus implementation

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P07-01 — documented MBR region values are 64-bit-style byte quantities but implementation narrows MBR sectors
Anchors:
- `docs/reference.rst` region-start/region-size: integer byte values with optional K/M/G/T binary suffixes.
- `docs/advanced.rst` boot-mbr-switch region configuration: byte-valued region split into two halves.
- `src/config_file.c::parse_slots()`.
- `src/mbr.c::get_raw_partition_entry()`.

Bounded proposition: the user-facing region contract does not state a 32-bit-sector bound at the point where the implementation narrows computed sector start/size to `guint32`.

Direct source fact: docs describe byte-valued region inputs with suffixes; implementation converts the 64-bit byte values to 32-bit sector counts.

Inferred consequence: the documented input domain appears broader than the representable MBR-sector domain unless another documented/frozen invariant supplies the missing bound.

Falsify/downgrade with: contemporaneous documentation/test/config validation that explicitly constrains boot-MBR start and half-size to <= `G_MAXUINT32` sectors.

### P07-02 — polling docs specify a lower bound relationship but no upper bound matching implementation arithmetic
Anchors:
- `docs/reference.rst` polling `interval-sec` / `max-interval-sec`.
- `docs/advanced.rst` linear backoff description.
- `src/config_file.c::parse_polling_section()`.
- `src/polling.c::polling_reschedule()`.

Bounded proposition: contemporaneous docs/config checks require a minimum interval and max>base, but expose no upper bound that prevents the implementation's integer multiplications from exceeding their intermediate representations.

Direct source fact: docs specify seconds and the relationship between base/max; implementation performs integer multiplication during seconds-to-ms conversion and later backoff.

Inferred consequence: an accepted/documented configuration can enter arithmetic outside the intended representable scheduling range unless an unstated bound exists.

Falsify/downgrade with: a contemporaneous documented bound, test oracle, or parser invariant that constrains all accepted values to the safe arithmetic domain.
