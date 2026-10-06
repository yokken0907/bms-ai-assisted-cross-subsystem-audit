# RAUC prospective transfer — B8 upstream-report triage and drafts v1.0.0

**Status: DRAFTS ONLY — nothing in this file has been submitted to RAUC.**

B8 is optional and is not a transfer-success criterion. Not every `STRONG_SOURCE_FINDING` is suitable for immediate upstream reporting.

## Triage

### Draft for possible upstream reporting
1. **C002 — boot-switch clear counter width**
   - direct source/type-width mechanism;
   - conditional threshold is comparatively ordinary (> range of `guint` byte counter);
   - localized fix/test opportunity;
   - no same-mechanism public prior found.

2. **C007 — polling seconds-to-milliseconds intermediate arithmetic**
   - configuration values above about 24.8 days can exceed signed 32-bit millisecond multiplication while still fitting `gint`;
   - direct parser→configuration→scheduler path;
   - no same-mechanism public prior found.

3. **C008a + C008b — binary-suffixed configuration parser validation**
   - same helper and likely one validation hardening;
   - C008a: trailing text is not rejected;
   - C008b: scaled unsigned value is not range-checked;
   - documentation states supported token formats;
   - no same-mechanism fix found.

### Hold / do not report now
- **C001:** strong source-level representability gap but requires large MBR-region geometry; keep bounded unless practical supported-domain evidence is obtained.
- **C003:** unsigned region-end overflow is a valid source arithmetic edge but lives near the guint64 limit; no practical physical-device relevance established.
- **C004:** contract-dependent on libnl/kernel disconnect semantics.
- **C005:** contract-dependent/tolerant status-file policy; historical design context narrows concern.
- **C006:** same-mechanism prior explicitly establishes intentional behavior; no defect report.
- **C009:** source arithmetic edge survives, but practical reachability requires an extremely large consecutive-failure count; no operational relevance claimed.

---

## Draft 1 — C002

### Title
`clear_boot_switch_partition() uses a guint byte counter for a guint64 partition size`

### Body

In the current master / audited commit `1a412fe80badb9cf91f5374ea2ef791de4db55a9`, `clear_boot_switch_partition()` in `src/update_handler.c` clears a `struct boot_switch_partition` whose `size` member is `guint64`, but tracks cleared bytes with:

```c
guint clear_count = 0;
...
while (clear_count < dest_partition->size) {
    ...
    clear_count += tmp_count;
}
```

The same helper is used by the boot-switch handlers after an inactive region/partition has been derived.

On an ABI where `guint` is 32-bit, a partition half larger than the `guint` range cannot be represented monotonically by `clear_count`; the counter can wrap while the 64-bit target remains larger.

A small separate width witness reproduces the bounded arithmetic mechanism:

```text
target=4294971391 before=4294967040 after_plus_512=256 monotonic=no
```

I did not find a source guard that constrains every call to `dest_partition->size <= G_MAXUINT`.

**Bounded question:** is such a size bound an intended supported-domain invariant? If not, using a 64-bit/off_t-compatible counter (and a regression test around the boundary) would avoid the width mismatch.

This report does not claim field incidence or safety impact.

---

## Draft 2 — C007

### Title
`polling interval seconds are multiplied as gint before assignment to gint64 milliseconds`

### Body

In `src/config_file.c::parse_polling_section()`, polling intervals are read as `gint`:

```c
gint interval_sec = key_file_consume_integer(...);
...
gint max_interval_sec = key_file_consume_integer(...);
...
c->polling_interval_ms = interval_sec * 1000;
c->polling_max_interval_ms = max_interval_sec * 1000;
```

The destination members are `gint64`, but the multiplication is formed from `gint` operands before assignment. The parser enforces a minimum interval and `max_interval_sec > interval_sec`, but I could not find a safe upper bound.

For example, `interval-sec=3000000` is representable by a 32-bit signed `gint`, while the mathematical millisecond value is 3,000,000,000, above `INT_MAX`.

The default maximum path also computes `interval_sec * 4` before the later millisecond conversion.

**Expected bounded behavior:** any accepted interval should be converted without overflowing the intermediate representation.

A possible approach would be to widen before multiplication and/or reject values above a documented maximum.

This report is limited to configuration arithmetic; it does not claim observed field failures.

---

## Draft 3 — C008a/C008b

### Title
`key_file_consume_binary_suffixed_string() does not validate token exhaustion or scaled-value overflow`

### Body

`src/utils.c::key_file_consume_binary_suffixed_string()` parses a decimal prefix using `g_ascii_strtoull()`, inspects the first non-digit character as an optional K/M/G/T suffix, and returns a shifted value:

```c
result = g_ascii_strtoull(string, &scale, 10);
...
return result << scale_shift;
```

I see two separable validation gaps in the same helper:

1. **Token exhaustion:** after recognizing the first suffix character, the function does not check that the token ends. A mirrored parser-structure witness accepts `1Kgarbage` as 1024 while leaving `Kgarbage` at the end pointer.
2. **Scaled range:** before `result << scale_shift`, the function does not check that the mathematical scaled value fits `guint64`. Unsigned left shift therefore can wrap modulo the destination width for sufficiently large values.

This helper is used for configuration values including boot-region sizes/starts and other binary-sized options. Current documentation describes decimal values with optional supported K/M/G/T suffixes.

**Bounded expected behavior:** malformed trailing text and values whose scaled result is not representable should be rejected rather than silently mapped to another numeric value.

A regression test could cover e.g. trailing characters after a suffix and a value above `G_MAXUINT64 >> scale_shift`.

No security, field-incidence, or safety claim is made here.
