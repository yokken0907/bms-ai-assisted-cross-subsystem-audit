# RAUC prospective transfer — B2–B6 source-only adjudication v1.0.0

Target: `rauc/rauc` @ `1a412fe80badb9cf91f5374ea2ef791de4db55a9`

No issue/PR/fix/advisory/candidate-specific web material was used. Public-prior status remains `NOT_SEARCHED` for every row. The findings below are source-only and bounded.

## Funnel

- B1 emitted proposals: 11
- B1 frozen candidates: 9
- B3 split: C008 -> C008a + C008b (original candidate count unchanged; analytical row count increases)
- B5 provisional-strong child/original rows: 7
- B6 separate/static checks executed for all 7 provisional-strong rows
- B6 final source-only dispositions: 7 `STRONG_SOURCE_FINDING`, 2 `CONTRACT_DEPENDENT`, 1 `INTENT_DEPENDENT_HOLD`; composite parent C008 is superseded by its two children and has no standalone terminal claim.

## Final source-only rows

| Row | B2/B3 summary | B5 | B6 | Source-only disposition |
|---|---|---|---|---|
| C001 | MBR 64->32-bit sector narrowing; path closed | PROVISIONAL_STRONG | executable representation witness PASS | STRONG_SOURCE_FINDING |
| C002 | guint clear counter vs guint64 partition size; path closed | PROVISIONAL_STRONG | executable width/wrap witness PASS | STRONG_SOURCE_FINDING |
| C003 | unchecked guint64 region-end addition; path closed | PROVISIONAL_STRONG | executable wrap witness PASS | STRONG_SOURCE_FINDING |
| C004 | NBD netlink failure normalized to success; external API intent unresolved | CONTRACT_DEPENDENT | not required | CONTRACT_DEPENDENT |
| C005 | status checksum size parsed without error channel; persistence contract unresolved | CONTRACT_DEPENDENT | not required | CONTRACT_DEPENDENT |
| C006 | activation metadata save failure does not change success; authority/intent unresolved | INTENT_DEPENDENT_HOLD | not required | INTENT_DEPENDENT_HOLD |
| C008 | composite parser candidate | NOT_EVALUABLE | split | superseded by C008a/C008b |
| C008a | trailing-token acceptance | PROVISIONAL_STRONG | separate parser-structure witness PASS | STRONG_SOURCE_FINDING |
| C008b | unchecked unsigned scale shift | PROVISIONAL_STRONG | executable unsigned-shift witness PASS | STRONG_SOURCE_FINDING |
| C007 | polling sec->ms intermediate signed-int range | PROVISIONAL_STRONG | static/widened arithmetic check PASS | STRONG_SOURCE_FINDING |
| C009 | polling backoff pre-clamp unsigned wrap | PROVISIONAL_STRONG | executable arithmetic witness PASS | STRONG_SOURCE_FINDING |

## Claim boundaries

`STRONG_SOURCE_FINDING` means only that the bounded frozen-source mechanism survived B2-B6 under the pre-frozen gates. It is not a claim of field incidence, exploitability, safety severity, hardware consequence, novelty, or maintainer acceptance.

C004-C006 remain intentionally unresolved rather than being promoted by design invention.

## Transfer-study status

The source-only pipeline itself has not required a new primary gate or terminal category. However, D001 already prevents a `CLEAN_TRANSFER` label because the third-party Software Heritage capture occurred after target selection. The study therefore has a predeclared transfer-outcome ceiling of `QUALIFIED_TRANSFER`, independent of bug yield.

B7 public-prior/current-state reconnaissance has **not** yet been run.
