# Reproduction guide

## 1. Quick integrity-only verification

```bash
python scripts/verify_all.py
```

Without an exact source archive this performs repository, paper, data, and witness-hash checks and reports a partial pass.

## 2. Full source-level reproduction

Online:
```bash
python scripts/verify_all.py --fetch-source --strict
```

Offline:
```bash
python scripts/verify_all.py --source-zip /path/to/foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip --strict
```

Expected source SHA-256: `2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2`.

The full run verifies all 25 source anchors, executes all 17 cases, checks `-O0/-O2` equality for C witnesses and repeat equality for Python/static witnesses, and confirms the fixed publication statistics.

## 3. Regenerate publication-facing summary tables

```bash
python scripts/generate_tables.py
```

The generated document is `generated/PUBLICATION_EVIDENCE_SUMMARY.md`.

## 4. Full Master-of-All archival verification

Download the release asset with SHA-256 `4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7`, then run:

```bash
python scripts/verify_master_of_all.py BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

The wrapper extracts the embedded full project archive and exact source to a temporary directory, creates a canonical sidecar for the temporary copy, then invokes the byte-preserved `scripts/frozen/verify_project_master_independent.py`. A successful run must report 22/22 gates PASS.

## Reproducibility target

The target is the preserved source/evidence/witness relationship, not reproduction of any prior AI conversation.
