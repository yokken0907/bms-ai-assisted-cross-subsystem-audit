# RAUC prospective transfer — B9 post-outcome adversarial closure v1.0.0

Date: 2026-10-07  
Target: `rauc/rauc`  
Frozen target commit: `1a412fe80badb9cf91f5374ea2ef791de4db55a9`

This phase rechecks the already frozen B1-B8 record. It does not rerun candidate generation and does not rewrite the historical B1/B6 artifacts.

## Result

The transfer outcome remains **QUALIFIED_TRANSFER**.

D001 already prevents CLEAN_TRANSFER because the third-party Software Heritage capture occurred after target selection. B9 found one additional post-outcome claim-strength correction affecting C001. No new primary gate or terminal category is needed.

## C001 correction

The direct local source fact remains valid: `src/mbr.c::get_raw_partition_entry()` narrows the 64-bit byte-valued `boot_switch_partition.start/size` to `guint32` sector counts without an explicit range check at the narrowing site.

However, B3 previously marked the configuration-to-write path CLOSED for the consequential out-of-range value domain. Re-reading the normal `boot-mbr-switch` sequence shows:

1. `r_mbr_switch_get_inactive_partition()`
2. `clear_boot_switch_partition()`
3. image write
4. `r_mbr_switch_set_boot_partition()`
5. `get_raw_partition_entry()`

To make the MBR narrowing consequential in the normal handler path, the inactive start or size must exceed `G_MAXUINT32` sectors. A concrete source-consistent geometry is:

- 512-byte sectors
- `region_start = 1,048,576` bytes (2,048 sectors)
- inactive start = exactly `2^32` sectors
- half size = `2,199,022,206,976` bytes
- full region size = `4,398,044,413,952` bytes

But `clear_boot_switch_partition()` executes first and tracks the multi-terabyte `guint64` target with `guint clear_count`. On the ordinary 32-bit-`guint` ABI, the counter cannot equal a target above `G_MAXUINT`; after wrap it remains below the 64-bit target. Thus the successful normal-handler path does not reach the consequential MBR re-encoding for this domain.

No alternate in-repository caller of `r_mbr_switch_set_boot_partition()` was found.

Therefore:

- local narrowing fact: retained;
- historical B3 CLOSED: overclaimed for consequential values;
- current post-outcome ceiling for C001: **CONTEXT_UNRESOLVED**;
- this is a downgrade, not a falsification of the local code fact.

## Other rows

No new material defeater was found for C002, C003, C004, C005, C006, C007, C008a, C008b, or C009 under their already bounded claims.

Historical B6:
- 7 STRONG_SOURCE_FINDING
- 2 CONTRACT_DEPENDENT
- 1 INTENT_DEPENDENT_HOLD

Post-B9 current interpretation:
- 6 STRONG_SOURCE_FINDING
- 1 CONTEXT_UNRESOLVED (C001)
- 2 CONTRACT_DEPENDENT
- 1 INTENT_DEPENDENT_HOLD

C008 remains a superseded composite parent and is not a standalone terminal claim.

## Methodological effect

The correction uses an already frozen category (`CONTEXT_UNRESOLVED`) and does not require a new gate/category. The final transfer label therefore remains QUALIFIED_TRANSFER.

The substantive lesson is that interacting candidate mechanisms can themselves become material reachability defeaters for another row. Evidence-gating controls claim escalation but does not eliminate adjudication error.

No RAUC issue is submitted by B9.
