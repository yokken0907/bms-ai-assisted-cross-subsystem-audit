# RAUC prospective transfer — B7 public-prior/current-state/context review v1.0.0

Target: `rauc/rauc` @ frozen commit `1a412fe80badb9cf91f5374ea2ef791de4db55a9`

## Ordering check

B7 was opened only after:
- B1 candidate freeze;
- B2-B5 source-only adjudication;
- B6 separate/static checks and source-only technical dispositions.

No B6 disposition has been overwritten.

## Mutable upstream state

At this review, the RAUC default branch `master` resolves to the **same commit as the frozen target**:

`1a412fe80badb9cf91f5374ea2ef791de4db55a9`

Therefore there is no post-freeze master change that can count as a current fix for any candidate.

## Prior-public dispositions

| Row | B6 source-only status | B7 prior-public | External context effect | Current master fix |
|---|---|---|---|---|
| C001 | STRONG_SOURCE_FINDING | RELATED_ONLY | NARROWS | No |
| C002 | STRONG_SOURCE_FINDING | RELATED_ONLY | NARROWS | No |
| C003 | STRONG_SOURCE_FINDING | RELATED_ONLY | NARROWS | No |
| C004 | CONTRACT_DEPENDENT | RELATED_ONLY | NONE | No |
| C005 | CONTRACT_DEPENDENT | RELATED_ONLY | CLARIFIES_INTENT | No |
| C006 | INTENT_DEPENDENT_HOLD | SAME_MECHANISM_PRIOR | CLARIFIES_INTENT | No |
| C007 | STRONG_SOURCE_FINDING | NO_MATCH_FOUND | NONE | No |
| C008a | STRONG_SOURCE_FINDING | RELATED_ONLY | SUPPORTS | No |
| C008b | STRONG_SOURCE_FINDING | RELATED_ONLY | NONE | No |
| C009 | STRONG_SOURCE_FINDING | NO_MATCH_FOUND | NARROWS | No |

`NO_MATCH_FOUND` is **not** a novelty claim.

## Most important external-context result

C006 is an exact demonstration of why source-only intent holds were preserved. Historical commit
`5bb3b500de87a6527cb34a086dc44ccde54311e2`
is titled **“src/mark: do not let mark_active() fail on failed status update”** and explicitly states the rationale: the installation/activation can already have succeeded even when writing status metadata fails, so the status-file error should be logged rather than make `mark_active()` fail.

Thus:
- B6 `INTENT_DEPENDENT_HOLD` remains the immutable source-only result;
- B7 records `SAME_MECHANISM_PRIOR` + `CLARIFIES_INTENT`;
- the post-external publication ceiling is **intentional behavior, not a defect report**.

This is not counted as a method failure; it is exactly the type of late external clarification the protocol separated from source truth.

## Candidate-specific notes

- **C001:** old MBR commits/PRs touch the same helper/module but concern different error paths or empty partition handling. No same-mechanism 64→32 sector-range prior was found. Claim narrowed to the missing representability guard, not ordinary field behavior.
- **C002:** prior material discusses clearing policy and other error handling, not the `guint` counter versus `guint64` target. No same-mechanism prior found.
- **C003:** prior MBR validation fixes exist, including a 2026 device-size/ioctl bug, but not the `region_start+region_size` unsigned-overflow mechanism.
- **C004:** NBD failures have prior history, but no public match was found for collapsing every negative disconnect-send result into local-success semantics. The row stays contract-dependent.
- **C005:** historical status-loading design favors tolerant/logging behavior, which narrows publication interpretation. No same size-field parse mechanism was found.
- **C007:** no candidate-specific public match found for the seconds→milliseconds intermediate signed-int range issue.
- **C008a/b:** a 2025 documentation commit made supported binary-suffixed formats explicit, but did not add full-token or scaled-value range validation. It is related public context, not a same-mechanism fix.
- **C009:** no candidate-specific public match found for pre-clamp polling-backoff wrap. Practical reachability remains deliberately unclaimed.

## Descriptive counts

Across the 10 terminal analytical rows after the C008 split:
- SAME_MECHANISM_PRIOR: 1
- RELATED_ONLY: 7
- NO_MATCH_FOUND: 2
- CURRENT_FIX_EXISTS: 0

External-context effects:
- CLARIFIES_INTENT: 2
- SUPPORTS: 1
- NARROWS: 4
- NONE: 3
- CONTRADICTS: 0

The transfer-study outcome ceiling remains `QUALIFIED_TRANSFER` because of preregistration-sequence deviation D001, independently of these candidate outcomes.

## B8 status

No RAUC issue has been opened by this prospective study. Upstream disposition remains `NOT_REPORTED` for all rows. B8 is optional and should operate on maintainer-facing bounded wording, not on the unqualified B1 proposals.
