# RAUC prospective transfer — final protocol outcome v1.0.0

## Primary question

Can the pre-frozen foxBMS-derived evidence-gating/claim-control protocol be applied to a new near-domain public C/C++ codebase without outcome-informed changes to its primary gate/category structure, while giving every frozen candidate a traceable source-only disposition and allowing zero strong findings?

## Result

**QUALIFIED_TRANSFER**

The protocol was operationally able to carry the frozen RAUC candidate cohort through B1-B7 without adding or changing a primary evidence gate or terminal source-only technical category. Every primary-eligible frozen candidate received a traceable source-only disposition. However, the study cannot be labeled CLEAN_TRANSFER because the third-party Software Heritage archival capture occurred after target-pool construction/target selection (D001), even though the public GitHub hash-manifest registration commit preceded selection and no B1 candidate generation had begun.

This outcome is fixed independently of defect yield.

## Target and source freeze

- target: `rauc/rauc`
- frozen/current upstream commit at B7: `1a412fe80badb9cf91f5374ea2ef791de4db55a9`
- filtered non-generated C/C++ LOC: 36,820
- C/C++ files: 67
- source-tar SHA-256: `f0e4c65831e4242709d262b2451745108d78bb83c6f42567b2d3cd0369d48cd6`
- complete non-.git file-manifest SHA-256: `7c0953624afee716c62ecebca37fc003f662b7c38a0266ac92e89636f549154e`

## Descriptive funnel

- B1 lens runs: 8/8, exactly one usable run each
- emitted proposals: 11
- B1 schema-rejected proposals: 1
- exact-mechanism duplicate merges: 1
- frozen original candidates: 9
- B3 split: 1 parent candidate (C008) -> 2 counterfactually separable child rows (C008a/C008b)
- terminal analytical rows after split: 10
- deferred discoveries outside the primary cohort: 0

### B6 source-only dispositions

- STRONG_SOURCE_FINDING: 7
- CONTRACT_DEPENDENT: 2
- INTENT_DEPENDENT_HOLD: 1
- other terminal categories: 0
- composite parent C008: superseded by split children, no standalone terminal claim

Rows with source-only residual material doubt: 3 (C004, C005, C006). B7 later clarified C006 intent without overwriting its B6 record.

### B7 prior-public status across 10 terminal rows

- SAME_MECHANISM_PRIOR: 1
- RELATED_ONLY: 7
- NO_MATCH_FOUND: 2
- CURRENT_FIX_EXISTS: 0

`NO_MATCH_FOUND` is not a novelty claim.

### Process / upstream axes

- target-level C3 contamination: 0
- primary original candidates excluded for contamination: 0
- major deviations: 1 (D001 preregistration-sequence deviation)
- minor deviations: 2 (D002/D003 B0 record-generation/workflow corrections)
- new primary gate required: No
- new terminal technical category required: No
- upstream reports submitted in this prospective study at outcome freeze: 0
- upstream disposition: NOT_REPORTED for all rows

## Important negative/clarifying result

C006 was held at B6 as `INTENT_DEPENDENT_HOLD`. B7 found historical RAUC commit
`5bb3b500de87a6527cb34a086dc44ccde54311e2`,
which explicitly introduced the current behavior and states that failed slot-status persistence should not make `mark_active()` fail because the installation/activation itself can already have succeeded.

This is recorded as:
- B6 source-only: INTENT_DEPENDENT_HOLD
- B7 prior-public: SAME_MECHANISM_PRIOR
- external-context effect: CLARIFIES_INTENT
- post-external ceiling: intentional behavior; no defect report

The late clarification is evidence that separating source truth, design intent, and public-history axes prevented a source-level ambiguity from being promoted into an unsupported defect claim.

## Interpretation

The result does **not** establish that the workflow is a generally validated detector. It shows only that, in one prospectively run near-domain case, the pre-frozen gate/category architecture was sufficient to process the frozen candidate cohort without outcome-driven structural changes.

The qualified rather than clean result is caused by registration sequencing, not by candidate yield or by a need to rescue the technical pipeline.

## Required validity threats

- single purposive near-domain case;
- foxBMS-derived lens overfitting;
- exploratory/nondeterministic AI candidate generation;
- unobservable LLM parametric-memory leakage;
- source/static witnesses do not reproduce integrated hardware/kernel/field behavior;
- documentation/test oracles may themselves be incomplete;
- public issue/commit history and maintainer evidence are uncontrolled external evidence;
- several strong source findings concern extreme or conditional input domains and are deliberately not equated with practical field defects;
- D001 prevents a clean claim of third-party preregistration before target selection.

## Claim ceiling

The strongest defensible methodological claim is:

> In this single near-domain RAUC case, a foxBMS-derived, pre-frozen evidence-gating and claim-control architecture was operationally sufficient to freeze, adjudicate, falsify/narrow, separately cross-check, and externally contextualize the candidate cohort without adding a new primary gate or terminal source-only category. Because third-party archival registration occurred after target selection, the study is classified as QUALIFIED_TRANSFER rather than CLEAN_TRANSFER.

No precision, false-positive rate, prevalence, detector superiority, safety impact, or broad external validity is inferred.
