# RAUC prospective transfer — final protocol outcome v1.0.1 (post-B9 correction)

This file supersedes the *current interpretation* of v1.0.0 without deleting or rewriting the historical frozen B1-B8 artifacts.

## Outcome

**QUALIFIED_TRANSFER** — unchanged.

The protocol architecture processed the frozen RAUC cohort without adding a new primary gate or terminal source-only category. D001 independently prevents CLEAN_TRANSFER because the third-party Software Heritage capture followed target selection.

B9 subsequently found one adjudication-level overstatement in C001. The correction uses the already frozen `CONTEXT_UNRESOLVED` category and therefore does not change the transfer label.

## Historical versus current source-only counts

Historical frozen B6:
- STRONG_SOURCE_FINDING: 7
- CONTRACT_DEPENDENT: 2
- INTENT_DEPENDENT_HOLD: 1

Post-B9 current interpretation:
- STRONG_SOURCE_FINDING: 6
- CONTEXT_UNRESOLVED: 1 (C001)
- CONTRACT_DEPENDENT: 2
- INTENT_DEPENDENT_HOLD: 1

C008 remains a superseded composite parent.

## C001 correction

The local 64-to-32-bit MBR sector narrowing remains a direct source fact. The post-outcome recheck found that the normal boot-mbr-switch path to *consequential* out-of-range narrowing is blocked earlier by C002's `guint` clear counter for the same large partition-size domain. The earlier B3 CLOSED assessment therefore overclaimed normal-handler reachability.

Current C001 ceiling: `CONTEXT_UNRESOLVED`.

## Strongest defensible methodological claim

> In this single near-domain RAUC case, the foxBMS-derived pre-frozen gate/category architecture was operationally sufficient to freeze and adjudicate the candidate cohort without inventing a new primary gate or terminal category. The study is QUALIFIED_TRANSFER rather than CLEAN_TRANSFER because third-party archival registration occurred after target selection. A post-outcome adversarial recheck found one path-closure adjudication error (C001), which was downgraded using an already predeclared category rather than by changing the architecture.

No detector-performance, prevalence, field-impact, safety, or broad external-validity claim is inferred.
