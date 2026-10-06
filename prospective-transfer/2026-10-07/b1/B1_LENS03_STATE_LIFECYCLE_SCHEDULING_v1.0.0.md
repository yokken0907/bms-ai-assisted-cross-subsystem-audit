# B1 Lens 03 — State / lifecycle / scheduling / initialization

Model/configuration: GPT-5.6 Sol / High thinking
Target: rauc/rauc
Frozen target commit: 1a412fe80badb9cf91f5374ea2ef791de4db55a9
Run status: single usable semantic run; no retry
Evidence restriction: frozen source/docs/tests/build material only; no issue/PR/fix/advisory or candidate-specific web material inspected.

Common prompt contract:
Inspect only the admissible frozen target material. Return at most five bounded, source-anchored propositions that may be internally inconsistent or contradicted by a current contract under this lens. For each: give exact path/symbol anchors, state the minimal falsifiable proposition, distinguish direct source fact from inferred consequence, and state what evidence would falsify or downgrade it. Do not infer field impact, safety severity, certification consequences, or preferred design. Return fewer or zero candidates if the source does not support them. Do not inspect or rely on issue/PR/fix history or candidate-specific web material. Prioritize direct anchoring and falsifiability, not drama or severity.

## Emitted proposals

### P03-01 — activation can report success after status persistence failure
Anchors:
- `src/mark.c::r_mark_active()`.
- status update performed after `r_boot_set_primary()`.

Bounded proposition: after successfully changing the bootloader primary slot, `r_mark_active()` updates activation timestamp/count and attempts to persist slot status, but a status-file write error is logged and does not make the function fail.

Direct source fact: the persistence error branch logs/frees `ierror` and execution continues; the function's failure path is tied to the bootloader-primary operation, not status persistence.

Inferred consequence: caller-visible success can coexist with failure to persist the activation metadata that the same function just updated in memory.

Falsify/downgrade with: a documented contract establishing activation metadata persistence as explicitly best-effort/non-authoritative, or a later source path that retries/guarantees persistence before success is exposed.
