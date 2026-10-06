# B1 Lens 01 — Interface / representation / unit contracts

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P01-01 — MBR partition fields receive narrowed sector counts
Anchors:
- `src/config_file.c::parse_slots()` — `region_start`/`region_size` are parsed as `guint64` byte values.
- `include/update_handler.h::struct boot_switch_partition` — start/size are `guint64` bytes.
- `src/mbr.c::get_raw_partition_entry()` — `partition->start / sector_size` and `partition->size / sector_size` are assigned to `guint32` before writing the 32-bit MBR fields.

Bounded proposition: the boot-MBR path has an explicit 64-bit-to-32-bit representation narrowing for start/size sector counts without a visible range check at the narrowing site.

Direct source fact: the values are carried as `guint64` bytes and narrowed to `guint32` sector counts.

Inferred consequence: configurations/device geometries whose sector start or sector size exceed `G_MAXUINT32` could be represented differently after the narrowing.

Falsify/downgrade with: a frozen-source invariant proving every reachable boot-MBR start/size in sectors is <= `G_MAXUINT32`, or language/toolchain evidence that the asserted narrowing cannot alter any reachable value.

### P01-02 — 64-bit partition size is cleared with a `guint` byte counter
Anchors:
- `include/update_handler.h::struct boot_switch_partition.size` — `guint64`.
- `src/update_handler.c::clear_boot_switch_partition()` — `guint clear_count`, compared with `dest_partition->size`, incremented by each write.

Bounded proposition: the clear loop tracks a `guint64` byte target using a `guint` counter.

Direct source fact: `clear_count` is `guint`; `dest_partition->size` is `guint64`.

Inferred consequence: for a reachable partition size above `G_MAXUINT`, the counter cannot monotonically represent all byte counts up to the target.

Falsify/downgrade with: a frozen-source reachability/invariant proving `dest_partition->size <= G_MAXUINT` for every call to this function, or evidence that `guint` is 64-bit in the supported execution contract.

### P01-03 — region-end validation adds two unbounded `guint64` values
Anchors:
- `src/utils.c::key_file_consume_binary_suffixed_string()` — returns `guint64`.
- `src/config_file.c::parse_slots()` — consumes region-start/region-size as `guint64`.
- `src/mbr.c::validate_region()` — checks `start + size`.
- `src/gpt.c::check_region()` — checks `region_start + region_size` and derives the end.

Bounded proposition: region-end checks form a `guint64` sum without an explicit pre-addition overflow guard.

Direct source fact: both operands are `guint64`; the cited checks add them directly.

Inferred consequence: if a reachable pair wraps modulo 2^64, a comparison against device size could evaluate a wrapped region end rather than the mathematical sum.

Falsify/downgrade with: a parser/configuration invariant that bounds the sum before these functions, or evidence that such near-limit values are rejected on every reachable path.
