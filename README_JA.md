# BMS AI-Assisted Cross-Subsystem Audit — 再現性リポジトリ

本リポジトリは、Keiji Yoshimuraによる論文 **“From Candidate Detection to Bounded Claims: A Reproducible AI-Assisted Cross-Subsystem Audit of Open-Source Battery Management Software”** とSupplement A/B/C（Version 1.1.1）の再現性資料である。論文本体とSupplementのDOCX/PDFはJxiv投稿・公開と分離するため、GitHubリポジトリには意図的に収録しない。

**Repository:** https://github.com/yokken0907/bms-ai-assisted-cross-subsystem-audit  
**Release v1.1.1:** https://github.com/yokken0907/bms-ai-assisted-cross-subsystem-audit/releases/tag/v1.1.1  
**Version 1.1.1 Release:** 2026-09-05公開済み。frozen Master-of-AllはGitHub Release assetとして取得できる。

目的は、固定されたfoxBMS 2ソースから、15件のbounded source-level candidate findings、2 controls、25 exact source anchors、witness replay、mitigation-pattern mapping、patent-document technical-pattern orientation、最終source-level dispositionまでを第三者が追跡・検証できるようにすることである。

## 重要な境界

15件は15個の実機製品欠陥、安全故障、脆弱性を意味しない。target hardware reachability、field occurrence、certification outcome、residual safety risk、patent novelty / infringement / patentability等も確立していない。

## 最短の再現方法

Python 3.10+、GCC(C11)、および `python -m pip install -r requirements.txt` で導入するmetadata検証用依存関係を使用する。

```bash
python scripts/verify_all.py --fetch-source --strict
```

既にexact source ZIPがある場合：

```bash
python scripts/verify_all.py --source-zip foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip --strict
```

これにより、repository integrity、固定集計値、witness hash、25 source anchors、15 candidates + 2 controlsの再実行を確認する。論文ファイルはGitHubに収録しないため、default verificationの対象外である。外部のVersion 1.1.1論文ファイルを保有している場合は、`scripts/verify_paper_hashes.py`でfinal bindingに記録されたcanonical hashと照合できる。

Master-of-Allを取得した場合は：

```bash
python scripts/verify_master_of_all.py BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```

で22 project-level gatesを再検証できる。ここでのverification separationはarchive builderとverifierの**実装分離**を意味し、外部研究機関による独立追試を意味しない。

詳細は英語版 `README.md`、`docs/REPRODUCTION_GUIDE.md`、`docs/CASE_NOTES.md` を参照。

## Release Asset identity確認

Publication SetはJxiv投稿・公開系統でGitHub外に保持する。一方、Master-of-Allは通常のGit追跡対象には含めず、公開済みVersion 1.1.1 GitHub Releaseのassetとして配布する。両方を取得した場合は、次でcanonical SHAと、Publication Set内8論文ファイルのfinal binding一致を確認できる。

```bash
python scripts/verify_release_assets.py --publication-set BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.1.zip --master-of-all BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip
```


## GitHub公開境界

GitHubには再現性repositoryのみを登録し、Main Manuscript、Supplement A/B/C、およびそれらを含むPublication Set ZIPは登録しない。論文artifactのSHA-256とrelease bindingのみをmetadataとして保持する。
