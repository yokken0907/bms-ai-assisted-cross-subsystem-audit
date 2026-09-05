# BMS AI-Assisted Cross-Subsystem Audit — Reproducibility Repository

Reproducibility repository for the manuscript **“From Candidate Detection to Bounded Claims: A Reproducible AI-Assisted Cross-Subsystem Audit of Open-Source Battery Management Software”** by Keiji Yoshimura.

**Repository:** https://github.com/yokken0907/bms-ai-assisted-cross-subsystem-audit  
**Release assets:** https://github.com/yokken0907/bms-ai-assisted-cross-subsystem-audit/releases  
**Version 1.1.1 release status:** release asset publication pending; the Git tree is prepared for the v1.1.1 public release.

This repository preserves the publication-facing evidence chain from a fixed foxBMS 2 source revision to 15 bounded source-level candidate findings, 2 controls, source-anchor verification, witness replay, mitigation-pattern mapping, patent-document technical-pattern orientation, and final source-level dispositions.

## Scope and claim boundary

The repository **does not** establish 15 deployed product defects, 15 vulnerabilities, or 15 safety failures. It does not establish target-hardware reachability, field occurrence, certification outcome, residual safety risk, patent novelty, infringement, patentability, validity, or freedom-to-operate. The 15 final conditions are reproducible **source-level candidate findings** within the frozen source/static/host-witness evidence base.

## Frozen source

- Project: foxBMS 2 v1.11.0
- Commit: `308028fb13d046ba29b98886895c2e17937b1437`
- Expected source ZIP SHA-256: `2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2`
- The upstream source is **not stored in the Git tree**. Use `python scripts/fetch_exact_source.py` or provide the exact ZIP yourself.

## Publication / GitHub distribution boundary

The manuscript and Supplements A/B/C are **intentionally not stored in this GitHub repository**. They are maintained as a separate Version 1.1.1 publication package for Jxiv submission/publication. This repository contains only the reproducibility materials needed to inspect the bounded evidence chain. Canonical publication-artifact hashes are retained in `release/FINAL_RELEASE_BINDING_v1.1.1.json` so that externally obtained publication files can later be checked without pre-distributing the manuscripts through GitHub.

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

1. repository integrity;
2. fixed publication-facing counts and cross-file invariants;
3. 15 candidate witness hashes and 2 control witnesses;
4. 25 exact source anchors against the frozen foxBMS source;
5. all 17 replay cases (15 candidates + 2 controls), including the candidate C-witness `-O0/-O2` consistency and two repeated Python/static checks.

Paper-file integrity is deliberately not part of the default GitHub repository check because manuscript files are not distributed here. If you possess the external Version 1.1.1 publication files, they can be checked against the recorded canonical hashes with `scripts/verify_paper_hashes.py`.

## Verify the full Master-of-All 22-gate archive

The complete Master-of-All is **not tracked in the normal Git tree**. It is distributed through GitHub Releases as the frozen scientific archive and is identified by its canonical SHA-256. For Version 1.1.1, use the release asset published under the v1.1.1 release once that release is posted. If downloaded alongside this repository:

```bash
python scripts/verify_master_of_all.py /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

The wrapper reconstructs the embedded project tree and invokes the byte-preserved, separately implemented project verifier from the frozen Master-of-All. “Separately implemented” here refers to implementation separation from the archive builder; it is **not external institutional or third-party replication**.

To verify the separately distributed publication package and frozen Master-of-All after obtaining them, run:

```bash
python scripts/verify_release_assets.py \
  --publication-set /path/to/BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.1.zip \
  --master-of-all /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

This checks the external Publication Set ZIP identity, verifies all eight publication files inside it against the canonical hashes recorded in the final binding, and checks the frozen Master-of-All identity. Neither the manuscripts nor the Publication Set ZIP are stored in the GitHub repository.

## Repository layout

- `data/` — publication-facing normalized registers and counts.
- `evidence/frozen/` — byte/content-preserved key JSON/MD evidence from Master-of-All and BMSA-12.
- `witnesses/` — 15 candidate witnesses, 2 controls, and required support files.
- `scripts/` — source acquisition, source-anchor verification, witness replay, invariant checks, and full verification orchestration.
- `generated/` — human-readable tables regenerated from machine-readable evidence.
- `release/` — release identities and cryptographic bindings for external assets not tracked in GitHub.
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

- Master-of-All SHA-256: `4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7` (frozen scientific archive; GitHub Release asset, not normal Git-tree content)
- Full project archive SHA-256: `b21d2e5078ddb95eb692c569e1f327b4d609ba72c99f34552d923448fa36479d`
- Publication Set v1.1.1 SHA-256 (external; not stored on GitHub): `4ea40c9798f6bf1cffbf247eb35cb3bd5f6f7da049a7ffc10492ec00e524a776`

## License status

No repository-wide license for the original audit material is selected by this packaging step. Upstream foxBMS software/documentation remains under its upstream licenses; see `third_party/` and `LICENSE_STATUS.md`.
