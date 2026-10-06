# B1 Lens 02 — Validity / error / sentinel propagation

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P02-01 — NBD disconnect send failures are normalized to success
Anchors:
- `src/nbd.c::r_nbd_remove_device()`.

Bounded proposition: any negative return from the NBD netlink disconnect send is treated as if the device were already removed, after which local state is cleared and the function returns `TRUE`.

Direct source fact: the `nl_send_sync(... ) < 0` branch only logs "nbd device is already removed"; execution then clears index/socket state and returns success.

Inferred consequence: a non-benign netlink send failure can be observationally collapsed into successful removal at this API boundary.

Falsify/downgrade with: a libnl/kernel contract showing every negative result reachable at this call means the device is already absent, or a documented RAUC contract that this routine is intentionally best-effort and callers must not interpret `TRUE` as kernel-side removal.

### P02-02 — status checksum size parse errors are discarded when a digest exists
Anchors:
- `src/status_file.c::status_file_get_slot_status()` (digest/size load block).
- `src/status_file.c::status_file_set_slot_status()` (digest/size serialization block).

Bounded proposition: when a stored SHA-256 string is present, the companion `size` is read with a NULL error channel and the resulting value is accepted into `slotstatus->checksum.size`.

Direct source fact: `g_key_file_get_uint64(..., "size", NULL)` is used without validating presence/parse success, whereas several nearby count fields explicitly process parse errors.

Inferred consequence: a malformed or missing stored size can be represented as the GLib fallback value while the checksum object still carries a digest/type.

Falsify/downgrade with: GLib contract evidence that this call cannot yield an accepted fallback on missing/invalid size, or frozen-source logic proving the size field is never consumed in a way that depends on its stored validity.
