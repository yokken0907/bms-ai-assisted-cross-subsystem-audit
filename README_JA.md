# BMS AI支援・サブシステム横断監査 — 再現性リポジトリ

本リポジトリは、Keiji Yoshimura による論文 **“From Candidate Detection to Bounded Claims: A Reproducible AI-Assisted Cross-Subsystem Audit of Open-Source Battery Management Software”** の再現性リポジトリです。

固定した foxBMS 2 ソース版から、15件の限定的な source-level candidate findings、2件の control、source-anchor verification、witness replay、mitigation-pattern mapping、patent-document technical-pattern orientation、最終 disposition までの publication-facing evidence chain を保存します。

## スコープと主張境界

本リポジトリは、15件の deployed product defects、15件の vulnerabilities、15件の safety failures を立証するものではありません。target-hardware reachability、field occurrence、certification outcome、residual safety risk、patent novelty、infringement、patentability、validity、freedom-to-operate も立証しません。15件の最終条件は、凍結した source/static/host-witness evidence base 内で再現可能な **source-level candidate findings** です。

## 固定ソース

- Project: foxBMS 2 v1.11.0
- Commit: `308028fb13d046ba29b98886895c2e17937b1437`
- Expected source ZIP SHA-256: `2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2`
- upstream source は Git tree に保存しません。`python scripts/fetch_exact_source.py` を使うか、exact ZIP を指定してください。

## 論文ファイルについて

Main Manuscript と Supplements A/B/C は、**Jxiv投稿前のため現在の公開Git treeには意図的に含めていません**。Version 1.1 のcanonical identityは `release/` と `PROVENANCE.json` にSHA-256で固定しています。Jxiv公開後は、Jxivの正式記録および／またはcanonical Publication Setをpublication-facing sourceとして参照できます。

## コア証拠の再現

必要環境：Python 3.10+、C11対応GCC。まず `python -m pip install -r requirements.txt` を実行してください。

```bash
python scripts/verify_all.py --fetch-source --strict
```

source ZIPを既に持っている場合：

```bash
python scripts/verify_all.py \
  --source-zip foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip \
  --strict
```

このコマンドは、Repository整合性、publication metadata invariants、15 candidate + 2 control witness、25 exact source anchors、17 replay cases を検証します。

4本のcanonical Version 1.1 DOCXを将来 `paper/` に追加した場合は、`python scripts/verify_paper_hashes.py` でも検証できます。現在のpre-publication public treeでは `paper/` が存在しないことは意図された状態であり、paper-file checkはoptional/skippedとして扱います。

## Master-of-All

完全なMaster-of-AllはGit treeではなくRelease Assetとして扱います。

```bash
python scripts/verify_master_of_all.py /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

canonical Publication Set と Master-of-All の両方をダウンロードした場合：

```bash
python scripts/verify_release_assets.py \
  --publication-set /path/to/BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.zip \
  --master-of-all /path/to/BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

この検証は、Publication Set ZIP identity と4本のcanonical DOCX hashを、Git treeに論文本体がなくても固定済みidentityに対して検証します。

## 主要ディレクトリ

- `data/` — publication-facing registers/counts
- `evidence/frozen/` — frozen evidence
- `witnesses/` — 15 candidate + 2 control witnesses
- `scripts/` — acquisition / verification / replay scripts
- `generated/` — machine-readable evidenceから再生成した表
- `release/` — Gitに置かない大容量assetのidentity
- `upstream/` — exact foxBMS source identity
- `third_party/` — upstream license notices
- `paper/` — Jxiv公開後にcanonical v1.1 DOCXを置く場合のoptional location。現在は意図的に不存在

## 解釈上の注意

- **BMSA05-F01:** witness comparatorは解析用であり、固定済み外部foxBMS requirementではありません。
- **BMSA10-F02:** public state-machine test-surface traceability candidateであり、statement/branch/MC/DC/transition coverageは測定していません。
- **BMSA03-F01:** “at least four transmissions” はfrozen timing assumptions下のupstream branch resultであり、本Publication Setで新規再導出したproject-level timing resultではありません。
- Patent documentsはtechnical-pattern orientation/mappingのみに用います。

## 大容量アーカイブの固定identity

- Master-of-All SHA-256: `4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7`
- Full project archive SHA-256: `b21d2e5078ddb95eb692c569e1f327b4d609ba72c99f34552d923448fa36479d`
- Publication Set v1.1 SHA-256: `5f783e651f3e64e2063a28c9bfc9337d7978f4421eee738290d01fa58fe47279`

詳細は `README.md`、`docs/CASE_NOTES.md`、`docs/CLAIM_BOUNDARY.md`、`release/RELEASE_ASSET_MANIFEST.json` を参照してください。
