# BMS AI-Assisted Cross-Subsystem Audit — Reproducibility Repository

Reproducibility repository for the manuscript **“From Candidate Detection to Bounded Claims: A Reproducible AI-Assisted Cross-Subsystem Audit of Open-Source Battery Management Software”** by Keiji Yoshimura.

This repository preserves the publication-facing evidence chain from a fixed foxBMS 2 source revision to 15 bounded source-level candidate findings, 2 controls, source-anchor verification, witness replay, mitigation-pattern mapping, patent-document technical-pattern orientation, and final source-level dispositions.

## Scope and claim boundary

The repository **does not** establish 15 deployed product defects, 15 vulnerabilities, or 15 safety failures. It does not establish target-hardware reachability, field occurrence, certification outcome, residual safety risk, patent novelty, infringement, patentability, validity, or freedom-to-operate. The 15 final conditions are reproducible **source-level candidate findings** within the frozen source/static/host-witness evidence base.

## Frozen source

- Project: foxBMS 2 v1.11.0
- Commit: `308028fb13d046ba29b98886895c2e17937b1437`
- Expected source ZIP SHA-256: `2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2`
- The upstream source is **not stored in the Git tree**. Use `python scripts/fetch_exact_source.py` or provide the exact ZIP yourself.

## Publication set

The `paper/` directory contains Main Manuscript + Supplements A/B/C, Version 1.1, with their published-package checksums.

## Reproduce the core publication evidence

Requirements: Python 3.10+ and GCC with C11 support. Install the small metadata-validation dependency first (`python -m pip install -r requirements.txt`). GCC with C11 support is also required for the C witnesses.

```bash
python scripts/verify_all.py --fetch-source --strict
```

Offline, if you already have the source ZIP:

```bash
python scripts/verify_all.py \
  --source-zip foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip \
  --strict
```

This command verifies:

1. repository and publication-file integrity;
2. fixed publication counts and cross-file invariants;
3. 15 candidate witness hashes and 2 control witnesses;
4. 25 exact source anchors against the frozen foxBMS source;
5. all 17 replay cases (15 candidates + 2 controls), including the candidate C-witness `-O0/-O2` consistency and two repeated Python/static checks.

## Verify the full Master-of-All 22-gate archive

The complete Master-of-All is intended as a release asset rather than a normal Git-tracked file. If downloaded alongside this repository:

```bash
python scripts/verify_master_of_all.py /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

The wrapper reconstructs the embedded project tree and invokes the byte-preserved, separately implemented project verifier from the frozen Master-of-All. “Separately implemented” here refers to implementation separation from the archive builder; it is **not external institutional or third-party replication**.

To verify both large release assets after downloading them, run:

```bash
python scripts/verify_release_assets.py \
  --publication-set /path/to/BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.zip \
  --master-of-all /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

This additionally checks the Publication Set ZIP identity and byte-equality of its four DOCX files against `paper/`.

## Repository layout

- `paper/` — publication Version 1.1.
- `data/` — publication-facing normalized registers and counts.
- `evidence/frozen/` — byte/content-preserved key JSON/MD evidence from Master-of-All and BMSA-12.
- `witnesses/` — 15 candidate witnesses, 2 controls, and required support files.
- `scripts/` — source acquisition, source-anchor verification, witness replay, invariant checks, and full verification orchestration.
- `generated/` — human-readable tables regenerated from machine-readable evidence.
- `release/` — identities of large release assets not tracked in Git.
- `upstream/` — exact foxBMS source identity.
- `third_party/` — upstream license notices needed for traceability of redistributed support material.

## Important publication-facing interpretation notes

- **BMSA05-F01:** the witness comparison is an explicit analysis comparator, not a frozen external foxBMS requirement.
- **BMSA10-F02:** this is a **public state-machine test-surface traceability candidate**; no statement/branch/MC/DC/transition coverage measurement was performed.
- **BMSA03-F01:** the “at least four transmissions” timing count is retained as an upstream branch result under its frozen timing assumptions, not as a newly re-derived project-level timing result.
- Patent documents are used only for **technical-pattern orientation/mapping**.

See `docs/CASE_NOTES.md` and `docs/CLAIM_BOUNDARY.md`.

## Large archival assets

The expected identities are recorded in `release/RELEASE_ASSET_MANIFEST.json`.

- Master-of-All SHA-256: `4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7`
- Full project archive SHA-256: `b21d2e5078ddb95eb692c569e1f327b4d609ba72c99f34552d923448fa36479d`
- Publication Set v1.1 SHA-256: `5f783e651f3e64e2063a28c9bfc9337d7978f4421eee738290d01fa58fe47279`

## License status

No repository-wide license for the original audit material is selected by this packaging step. Upstream foxBMS software/documentation remains under its upstream licenses; see `third_party/` and `LICENSE_STATUS.md`.
