#!/usr/bin/env python3
"""Build the archival Master-of-All package for BMSA-01 through BMSA-14."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any


MASTER_ROOT = "BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0"
MASTER_ZIP = f"{MASTER_ROOT}.zip"
STATUS_FILE = f"{MASTER_ROOT}_STATUS_REPORT.md"
DELIVERY_MANIFEST = f"{MASTER_ROOT}_DELIVERY_MANIFEST.json"
EXPECTED_PROJECT_ARCHIVE_SHA256 = "b21d2e5078ddb95eb692c569e1f327b4d609ba72c99f34552d923448fa36479d"
EXPECTED_PROJECT_FILES = 810
EXPECTED_PROJECT_ZIPS = 383
EXPECTED_SOURCE_SHA256 = "2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2"
EXACT_SOURCE_COMMIT = "308028fb13d046ba29b98886895c2e17937b1437"


BRANCHES: list[dict[str, Any]] = [
    {
        "branch_id": "BMSA-01",
        "directory": "BMSA_01",
        "scope": "Measurement chain",
        "artifact_role": "CANONICAL_AUDITED_CLOSEOUT",
        "canonical_artifact": "BMS_TECHNOLOGY_AUDIT_BMSA01_PHASE5_v0.6.2_AUDITED_CLOSEOUT.zip",
        "sha256": "9a0cd9663859687d8947cece1acf3967bdaa91db071cffc4ccb75c12557fc48e",
        "final_status": "CURRENT_EVIDENCE_BOUNDARY_CLOSED_WITH_REOPEN_GATE",
        "bounded_summary": "The exact IVT-S range remained unresolved; the measurement weakness candidate remains unquantified. No numerical behavior, safety effect, residual weakness, or novelty was established.",
    },
    {
        "branch_id": "BMSA-02",
        "directory": "BMSA_02",
        "scope": "State estimation",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA02_STATE_ESTIMATION_MASTER_REFERENCE_PACKAGE_v1.0.0.zip",
        "sha256": "d1257fdde252f8d768b0b9de99248ad2b9f726ffd6508d26fe2dc8ffb58f9982",
        "final_status": "CLOSED_NO_RESIDUAL_WEAKNESS_ESTABLISHED",
        "bounded_summary": "Known estimator dependencies and mitigations were mapped. Available public evidence did not establish a residual weakness.",
    },
    {
        "branch_id": "BMSA-03",
        "directory": "BMSA_03",
        "scope": "Operating limits",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA03_OPERATING_LIMITS_MASTER_REFERENCE_PACKAGE_v1.0.0.zip",
        "sha256": "7aee6428f03082d44d8dfb393945aff06ba5c84c507cf3eb2716bb3313008e3d",
        "final_status": "CLOSED_WITH_BOUNDED_WEAKNESS_CANDIDATE",
        "bounded_summary": "A static SOF validity-propagation candidate reaches CAN PackLimits; no receiver contract or unsafe behavior was established.",
    },
    {
        "branch_id": "BMSA-04",
        "directory": "BMSA-04",
        "scope": "Cell balancing",
        "artifact_role": "CANONICAL_AUDITED_CLOSEOUT",
        "canonical_artifact": "BMS_TECHNOLOGY_AUDIT_BMSA04_v1.6.2_AUDITED_CLOSEOUT.zip",
        "sha256": "234f9d2ead593801db5cdce943b658e5f0b63daa149be1af0da348a58bc94fb4",
        "final_status": "CLOSED_WITH_ROUTE_SPECIFIC_BOUNDED_SOFTWARE_WEAKNESS_CANDIDATE",
        "bounded_summary": "A HISTORY/SOC non-default-route candidate remains. The default voltage/LTC6813 route closes before hardware actuation; no physical or safety consequence was established.",
    },
    {
        "branch_id": "BMSA-05",
        "directory": "BMSA-05",
        "scope": "Charge control",
        "artifact_role": "CANONICAL_FINAL_CLOSURE",
        "canonical_artifact": "BMS_TECHNOLOGY_AUDIT_BMSA05_FINAL_CLOSURE_v1.2.0.zip",
        "sha256": "b8bba89ca9f88bc0a6d2d8ae687c5494587ea76692b76b23478e5d1b9aca7b8a",
        "final_status": "CLOSED_WITH_BOUNDED_SOFTWARE_CONFIGURATION_WEAKNESS_CANDIDATE",
        "bounded_summary": "NORMAL and CHARGE open-wire controls are distinct while the audited charge executive uses common NORMAL state. Deployment and physical outcomes were not established.",
    },
    {
        "branch_id": "BMSA-06",
        "directory": "BMSA-06",
        "scope": "Thermal sensing and diagnostic semantics",
        "artifact_role": "CANONICAL_FINAL_PHASE_CLOSEOUT",
        "canonical_artifact": "BMS_TECHNOLOGY_AUDIT_BMSA06_PHASE5_v0.6.6_AUDITED_CLOSEOUT.zip",
        "sha256": "35695fb5e7d3a7cf1f7655c565b0ae279860246c51c9b026ba5f97fe1ac175c0",
        "final_status": "PHASE5_CLOSED_PASS_BOUNDED_SOFTWARE_REACHABILITY",
        "candidate_disposition": "SURVIVES_AS_BOUNDED_SOFTWARE_WEAKNESS_CANDIDATE_AT_HOST_UNIT_AND_DIAGNOSTIC_CONTRACT_SCOPE",
        "bounded_summary": "The acquisition/value path into zero valid temperatures was supported at public-source scope; the Phase4 bounded candidate was not withdrawn. Physical reachability and unsafe thermal behavior were not established.",
    },
    {
        "branch_id": "BMSA-07",
        "directory": "BMSA-07",
        "scope": "Fault diagnosis",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA07_FAULT_DIAGNOSIS_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "sha256": "7bd657017e159d9a3355643b51c9ee688f25f67de66b3892fcc13a52661c238c",
        "final_status": "CLOSED_WITH_BOUNDED_SOURCE_LEVEL_DIAGNOSTIC_CONFIGURATION_WEAKNESS_CANDIDATE",
        "bounded_summary": "DIAG_DELAY_2000ms resolves to 1000u and reaches two fatal response-diagnostic channels and BMS delay consumption. Intent, deployment, timing, and safety effects were not established.",
    },
    {
        "branch_id": "BMSA-08",
        "directory": "BMSA-08",
        "scope": "Supervisory state machine",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA08_SUPERVISORY_STATE_MACHINE_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "sha256": "2a0d3ffe60678a93fda9b78adea01fcb59f9352b3fa886ec7a3415264057632e",
        "final_status": "CLOSED_WITH_TWO_BOUNDED_SOURCE_LEVEL_SUPERVISORY_CONTROL_WEAKNESS_CANDIDATES",
        "bounded_summary": "Open-wire Boolean-index collapse and a configuration-dependent multi-string connection self-loop survived. Hardware, deployment, and safety effects were not established.",
    },
    {
        "branch_id": "BMSA-09",
        "directory": "BMSA-09",
        "scope": "Communications and distributed BMS",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA09_COMMUNICATIONS_DISTRIBUTED_BMS_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "sha256": "24bc35d3c6c0d412751c8d55c625887f796f34751ec78e38966971185879221d",
        "final_status": "CLOSED_WITH_THREE_BOUNDED_ROUTE_SPECIFIC_SOURCE_LEVEL_COMMUNICATION_WEAKNESS_CANDIDATES",
        "bounded_summary": "Three route-specific candidates cover debug-CAN AFE fragment staleness, aerosol counter/CRC acceptance semantics, and optional IMD ACK-wait liveness. Default enablement and physical consequences were not established.",
    },
    {
        "branch_id": "BMSA-10",
        "directory": "BMSA-10",
        "scope": "Software assurance",
        "artifact_role": "CANONICAL_AMENDED_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA10_SOFTWARE_ASSURANCE_MASTER_REFERENCE_PACKAGE_v1.0.3.zip",
        "sha256": "c12bf680baf458b705783a664f96ac7afc5decb87b3596d7a89c69775daa9d7f",
        "final_status": "BMSA10_CLOSED",
        "scientific_status": "CLOSED_WITH_THREE_BOUNDED_SOURCE_LEVEL_SOFTWARE_ASSURANCE_WEAKNESS_CANDIDATES",
        "supersedes": "BMSA10_SOFTWARE_ASSURANCE_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "supersession_scope": "closure-lineage completeness only",
        "bounded_summary": "Three frozen headline findings remain; three deferred assurance items were dispositioned as non-headline public-test-adequacy gaps. No certification, deployment, product, or safety conclusion was added.",
    },
    {
        "branch_id": "BMSA-11",
        "directory": "BMSA-11",
        "scope": "Aging and parameter adaptation",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA11_AGING_PARAMETER_ADAPTATION_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "sha256": "590a983de6f823ae337fb86ce5c1cf37bbeb82bfa13370be75379aae24b70f64",
        "final_status": "CLOSED_WITH_ONE_BOUNDED_SOURCE_LEVEL_SOH_REPORTING_INTEGRATION_WEAKNESS_CANDIDATE",
        "bounded_summary": "The audited default CAN state-estimation callbacks report fixed 100% SOH rather than the SOH database path. Deployed CAN values, receiver use, intent, and safety effects were not established.",
    },
    {
        "branch_id": "BMSA-12",
        "directory": "BMSA-12",
        "scope": "Unified reproduction and stress harness",
        "artifact_role": "CANONICAL_AMENDED_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA12_UNIFIED_REPRODUCTION_STRESS_HARNESS_MASTER_REFERENCE_PACKAGE_v1.0.3.zip",
        "sha256": "d8000ef499b29af4ffcf71e23abd2a93a504bac25d6f19babe2d7d06437efed3",
        "final_status": "BMSA12_CLOSED",
        "scientific_status": "CLOSED_17_CASE_UNIFIED_REPRODUCTION_PASS_UPSTREAM_CANDIDATE_INVENTORY_COMPLETENESS_DEFECT_CORRECTED_NO_NEW_CROSS_BRANCH_WEAKNESS_ESTABLISHED",
        "supersedes": "BMSA12_UNIFIED_REPRODUCTION_STRESS_HARNESS_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "supersession_scope": "upstream candidate inventory completeness only",
        "bounded_summary": "Fifteen upstream candidates and two controls were resolved in separate lanes. No causal compound execution or new cross-branch weakness was established.",
    },
    {
        "branch_id": "BMSA-13",
        "directory": "BMSA-13",
        "scope": "Existing mitigation and patent map",
        "artifact_role": "CANONICAL_AMENDED_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA13_EXISTING_MITIGATION_PATENT_MAP_MASTER_REFERENCE_PACKAGE_v1.0.3.zip",
        "sha256": "4fd5e1a1dc7204cb7834306d78c06c320668bc062ea0f20d6e3baa8604160097",
        "final_status": "BMSA13_CLOSED",
        "supersedes": "BMSA13_EXISTING_MITIGATION_PATENT_MAP_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "supersession_scope": "BMSA09-F03 patent technical-pattern mapping accuracy only",
        "bounded_summary": "All 15 classifications and mitigation dispositions remained frozen. Candidate-specific validated mitigations were zero; novelty remained undetermined and no legal opinion was made.",
    },
    {
        "branch_id": "BMSA-14",
        "directory": "BMSA-14",
        "scope": "Residual gap determination",
        "artifact_role": "CANONICAL_MASTER_REFERENCE_PACKAGE",
        "canonical_artifact": "BMSA14_RESIDUAL_GAP_DETERMINATION_MASTER_REFERENCE_PACKAGE_v1.0.2.zip",
        "sha256": "8156c9227fa64c82b9589e480fdcd3ba760ee46271fac5baa19f6dab0aff3dce",
        "final_status": "BMSA14_CLOSED",
        "scientific_status": "CLOSED_15_BOUNDED_SOURCE_LEVEL_RESIDUAL_GAP_CANDIDATES_NO_PRODUCT_SAFETY_OR_RESIDUAL_RISK_DETERMINATION",
        "bounded_summary": "All 15 handoff candidates persist only as bounded source-level residual-gap candidates. This is not a residual-risk determination; upstream classifications were unchanged.",
    },
]


STATUS_REPORT_SOURCES = {
    "BMSA-07": "BMSA-07/BMSA07_STATUS_REPORT.md",
    "BMSA-08": "BMSA-08/BMSA08_STATUS_REPORT.md",
    "BMSA-09": "BMSA-09/BMSA09_STATUS_REPORT.md",
    "BMSA-10": "BMSA-10/BMSA10_STATUS_REPORT_v1.0.3.md",
    "BMSA-11": "BMSA-11/BMSA11_STATUS_REPORT.md",
    "BMSA-12": "BMSA-12/BMSA12_STATUS_REPORT_v1.0.3.md",
    "BMSA-13": "BMSA-13/BMSA13_STATUS_REPORT_v1.0.3.md",
    "BMSA-14": "BMSA-14/BMSA14_STATUS_REPORT.md",
}


CURATED_BMSA14_MEMBERS = [
    "BMSA13_MITIGATION_MAP_FROZEN.json",
    "BMSA13_PATENT_MAP_FROZEN.json",
    "CANDIDATE_SPECIFIC_MITIGATION_AUDIT_15_CASES.json",
    "CROSS_CASE_LEDGER_15_CASES.json",
    "HANDOFF_REGISTER_15_CASES.json",
    "RESIDUAL_GAP_DETERMINATIONS_15_CASES.json",
    "RESIDUAL_PERSISTENCE_REPLAY_15_CASES.json",
    "SOURCE_ANCHOR_VERIFICATION_15_CASES.json",
    "WITNESS_SHA256_LINEAGE_15_CASES.json",
    "SHA256_LINEAGE.json",
    "FINAL_FINDINGS.json",
]


EXPECTED_SIDECAR_ANOMALY_PATHS = {
    "BMSA-04/BMS_TECHNOLOGY_AUDIT_BMSA04_HISTORY_SOC_PHASE2C_v0.5.0_RESULTS_FOR_REVIEW.zip",
    "BMSA-04/BMS_TECHNOLOGY_AUDIT_BMSA04_HISTORY_SOC_PHASE2D_v0.6.0_RESULTS_FOR_REVIEW.zip",
    "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_v0.4.2_CORRECTED_CLOSEOUT_RESULTS_FOR_REVIEW.zip",
    "BMSA-06/BMS_TECHNOLOGY_AUDIT_BMSA06_PHASE5_v0.6.4_RUN02R_EXACT_ACQUISITION_BRIDGE_STARTER (1).zip",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def file_inventory(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return records


def parse_sidecar(zip_path: Path) -> dict[str, Any]:
    sidecar = zip_path.with_name(zip_path.name + ".sha256")
    if not sidecar.is_file():
        return {"status": "MISSING", "sidecar": None}
    text = sidecar.read_text(encoding="utf-8", errors="replace").strip()
    fields = text.split(maxsplit=1)
    declared_hash = fields[0] if fields else None
    declared_name = fields[1].strip() if len(fields) > 1 else None
    actual_hash = sha256_file(zip_path)
    if declared_hash != actual_hash:
        status = "HASH_MISMATCH"
    elif declared_name != zip_path.name:
        status = "NAME_ANOMALY_HASH_MATCH"
    else:
        status = "PASS"
    return {
        "status": status,
        "sidecar": sidecar.name,
        "declared_sha256": declared_hash,
        "actual_sha256": actual_hash,
        "declared_name": declared_name,
    }


def root_manifest_name(names: list[str]) -> str:
    candidates = [name for name in names if name == "MANIFEST.json" or name.endswith("/MANIFEST.json")]
    require(candidates, "ZIP lacks MANIFEST.json")
    return min(candidates, key=lambda name: name.count("/"))


def inspect_inner_zip(path: Path, project_root: Path) -> dict[str, Any]:
    manifest_errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        crc_bad = archive.testzip()
        names = [name for name in archive.namelist() if not name.endswith("/")]
        manifest_name = root_manifest_name(names)
        prefix = manifest_name[: -len("MANIFEST.json")]
        manifest = json.loads(archive.read(manifest_name))
        expected = {manifest_name}
        for record in manifest.get("files", []):
            member = prefix + record["path"]
            expected.add(member)
            if member not in names:
                manifest_errors.append(f"missing:{member}")
                continue
            data = archive.read(member)
            if len(data) != record["bytes"] or sha256_bytes(data) != record["sha256"]:
                manifest_errors.append(f"mismatch:{member}")
        for extra in sorted(set(names) - expected):
            manifest_errors.append(f"unmanifested:{extra}")
    sidecar = parse_sidecar(path)
    return {
        "path": path.relative_to(project_root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "crc_pass": crc_bad is None,
        "crc_bad_member": crc_bad,
        "root_manifest": manifest_name,
        "manifest_pass": not manifest_errors,
        "manifest_errors": manifest_errors,
        "sidecar": sidecar,
    }


def verify_project_archive(archive_path: Path, project_root: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        members = {name for name in archive.namelist() if not name.endswith("/")}
        expected = {f"{project_root.name}/{record['path']}" for record in records}
        if members != expected:
            errors.append("member_set_mismatch")
        for record in records:
            member = f"{project_root.name}/{record['path']}"
            if member not in members:
                continue
            data = archive.read(member)
            if len(data) != record["bytes"] or sha256_bytes(data) != record["sha256"]:
                errors.append(f"content_mismatch:{record['path']}")
    return {
        "archive": archive_path.name,
        "sha256": sha256_file(archive_path),
        "expected_sha256": EXPECTED_PROJECT_ARCHIVE_SHA256,
        "crc_pass": bad is None,
        "member_count": len(members),
        "member_set_and_content_equal_to_tree": not errors,
        "errors": errors,
        "pass": bad is None and not errors and sha256_file(archive_path) == EXPECTED_PROJECT_ARCHIVE_SHA256,
    }


def copy_with_sidecar(source: Path, destination_dir: Path) -> tuple[Path, Path]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    target = destination_dir / source.name
    shutil.copy2(source, target)
    source_sidecar = source.with_name(source.name + ".sha256")
    require(source_sidecar.is_file(), f"missing sidecar for {source}")
    target_sidecar = destination_dir / source_sidecar.name
    shutil.copy2(source_sidecar, target_sidecar)
    return target, target_sidecar


def extract_curated_bmsa14(master: Path, destination: Path) -> None:
    with zipfile.ZipFile(master) as archive:
        root = min(name.split("/", 1)[0] for name in archive.namelist() if not name.endswith("/"))
        for basename in CURATED_BMSA14_MEMBERS:
            member = f"{root}/{basename}"
            require(member in archive.namelist(), f"missing BMSA14 curated member: {basename}")
            target = destination / basename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(member))


def build_readme() -> str:
    return """# BMS Technology Audit — Master of All v1.0.0

このパッケージはBMSA-01〜BMSA-14の既存科学結果を変更せず、canonical成果物、最終全体archive、exact source、横断台帳、完全性証拠を一つに束ねた最終アーカイブです。

## 入口

- `PROJECT_CLOSURE_SUMMARY.md`: プロジェクト全体の短い結論
- `BRANCH_CLOSURE_LEDGER.json`: 14枝の最終statusとcanonical SHA-256
- `CROSS_BRANCH/`: 15候補のhandoff・再現・mitigation・residual-gap台帳
- `FULL_PROJECT_ARCHIVE/`: byte-preservedな全810ファイル版
- `CANONICAL_BRANCH_ARTIFACTS/`: 各枝のcanonical closeout/master
- `EXACT_SOURCE/`: 固定したfoxBMS source ZIP
- `INTEGRITY/`: tree、全383内包ZIP、既知包装異常、SHA-256の監査記録

## 解釈上の注意

BMSA-14の15件は `bounded source-level residual-gap candidates` であり、residual safety risk、製品欠陥、field failure、認証不適合を意味しません。既存の科学分類・claim boundary・supersession lineageは変更していません。
"""


def build_summary() -> str:
    return f"""# BMS Technology Audit — Project Closure Summary

## Archival status

`ARCHIVAL_INTEGRATION_COMPLETE_BMSA01_TO_BMSA14_CANONICAL_LINEAGE_VERIFIED`

- BMSA-01〜14: 14/14の宣言済み証拠範囲を最終dispositionまで記録
- canonical project tree: {EXPECTED_PROJECT_FILES} files / {EXPECTED_PROJECT_ZIPS} inner ZIPs
- exact source: foxBMS 2 v1.11.0, commit `{EXACT_SOURCE_COMMIT}`
- exact source ZIP SHA-256: `{EXPECTED_SOURCE_SHA256}`
- full project archive SHA-256: `{EXPECTED_PROJECT_ARCHIVE_SHA256}`

## Cross-branch result

- BMSA-12 registry: 15 upstream candidates + 2 controls = 17/17 resolved
- BMSA-13: candidate-specific validated mitigations 0; novelty `UNDETERMINED`; legal opinion false
- BMSA-14: 15/15 persist only as `PERSISTS_AS_BOUNDED_SOURCE_LEVEL_RESIDUAL_GAP_CANDIDATE`
- upstream classification changes: 0
- residual weakness declared: 0
- residual risk declared: 0
- cross-case causal compound execution established: false

## Integrity qualification

All 383 inherited scientific ZIPs pass CRC and contain a root manifest. Six inherited packaging-record anomalies are preserved and explicitly ledgered: four sidecar-name/presence anomalies and two manifest-record anomalies. No canonical branch artifact is affected, and the full archive is byte-identical to the 810-file project tree.

## Evidence ceiling

The project establishes bounded public-source semantics, host-unit/static witnesses, configuration/test-adequacy observations, and archival lineage. It does not establish deployed-binary behavior, target/HIL behavior, physical battery or contactor effects, field incidence, product safety outcome, certification status, OEM defect, novelty, patentability, or legal conclusions.
"""


CLAIM_BOUNDARY = """# Project-wide claim boundary

Permitted project-level statements are limited to exact public-source identity, deterministic source semantics, bounded host/static witness results, public-test adequacy gaps, configuration inconsistencies, candidate mappings, and cryptographic/archival lineage.

The package does not establish functional-safety certification failure, ISO 26262 non-compliance, an unsafe deployed BMS, a field failure, an OEM defect, production-vehicle impact, battery-fire risk, physical reachability, cross-case causal compound failure, novelty, patentability, infringement, invalidity, or any other legal conclusion.

`PERSISTS_AS_BOUNDED_SOURCE_LEVEL_RESIDUAL_GAP_CANDIDATE` means only that the frozen upstream candidate condition was not closed by a candidate-specific validated mitigation at the audited source/witness scope. It is not a residual-risk classification.
"""


def deterministic_zip(source_root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source_root.parent).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 8, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(args: argparse.Namespace) -> None:
    project_root = args.project_tree.resolve()
    project_archive = args.project_archive.resolve()
    source_zip = args.source_zip.resolve()
    work_dir = args.work_dir.resolve()
    output_dir = args.output_dir.resolve()

    require(project_root.is_dir(), "project tree missing")
    require(project_archive.is_file(), "project archive missing")
    require(source_zip.is_file(), "source ZIP missing")
    require(sha256_file(project_archive) == EXPECTED_PROJECT_ARCHIVE_SHA256, "project archive SHA mismatch")
    require(sha256_file(source_zip) == EXPECTED_SOURCE_SHA256, "exact source SHA mismatch")
    with zipfile.ZipFile(source_zip) as archive:
        require(archive.testzip() is None, "exact source ZIP CRC failure")

    tree_records = file_inventory(project_root)
    require(len(tree_records) == EXPECTED_PROJECT_FILES, f"project file count mismatch: {len(tree_records)}")
    inner_paths = sorted(project_root.rglob("*.zip"))
    require(len(inner_paths) == EXPECTED_PROJECT_ZIPS, f"project inner ZIP count mismatch: {len(inner_paths)}")
    archive_verification = verify_project_archive(project_archive, project_root, tree_records)
    require(archive_verification["pass"], "project archive does not match tree")

    inner_records = [inspect_inner_zip(path, project_root) for path in inner_paths]
    require(all(record["crc_pass"] for record in inner_records), "inner ZIP CRC failure")
    sidecar_anomalies = [record for record in inner_records if record["sidecar"]["status"] != "PASS"]
    manifest_anomalies = [record for record in inner_records if not record["manifest_pass"]]
    require({record["path"] for record in sidecar_anomalies} == EXPECTED_SIDECAR_ANOMALY_PATHS, "unexpected sidecar anomaly set")
    require(len(manifest_anomalies) == 2, "unexpected manifest anomaly count")
    require(
        {record["path"] for record in manifest_anomalies}
        == {
            "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_REFERENCE_AUDIT_v0.4.1_STARTER.zip",
            "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_v0.4.2_CORRECTED_CLOSEOUT_RESULTS_FOR_REVIEW.zip",
        },
        "unexpected manifest anomaly set",
    )

    branch_records = []
    for branch in BRANCHES:
        source = project_root / branch["directory"] / branch["canonical_artifact"]
        require(source.is_file(), f"canonical artifact missing: {source}")
        require(sha256_file(source) == branch["sha256"], f"canonical SHA mismatch: {branch['branch_id']}")
        sidecar = parse_sidecar(source)
        require(sidecar["status"] == "PASS", f"canonical sidecar failure: {branch['branch_id']}")
        with zipfile.ZipFile(source) as archive:
            require(archive.testzip() is None, f"canonical ZIP CRC failure: {branch['branch_id']}")
        enriched = dict(branch)
        enriched["project_relative_path"] = f"{branch['directory']}/{branch['canonical_artifact']}"
        enriched["bytes"] = source.stat().st_size
        enriched["canonical_sidecar_status"] = "PASS"
        branch_records.append(enriched)

    if work_dir.exists():
        shutil.rmtree(work_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    root = work_dir / MASTER_ROOT
    root.mkdir(parents=True)
    output_dir.mkdir(parents=True)

    write_text(root / "README_JA.md", build_readme())
    write_text(root / "PROJECT_CLOSURE_SUMMARY.md", build_summary())
    write_text(root / "CLAIM_BOUNDARY.md", CLAIM_BOUNDARY)
    write_text(
        root / "AI_ASSISTANCE_DISCLOSURE.md",
        "# AI assistance disclosure\n\nOpenAI Codex assisted with inventory reconstruction, hashing, ZIP/manifest verification, cross-branch indexing, deterministic packaging, and independent verification. No target hardware, HIL, deployed system, field dataset, certification audit, or legal review was performed.\n",
    )
    write_json(
        root / "EXACT_SOURCE_IDENTITY.json",
        {
            "project": "foxBMS 2",
            "version": "v1.11.0",
            "commit": EXACT_SOURCE_COMMIT,
            "source_zip": source_zip.name,
            "source_zip_bytes": source_zip.stat().st_size,
            "source_zip_sha256": EXPECTED_SOURCE_SHA256,
            "identity_pass": True,
        },
    )
    write_json(root / "BRANCH_CLOSURE_LEDGER.json", {"branch_count": 14, "records": branch_records})
    write_json(
        root / "PROJECT_MASTER_INDEX.json",
        {
            "package": MASTER_ROOT,
            "purpose": "ARCHIVAL_INTEGRATION_ONLY_NO_SCIENTIFIC_RESULT_CHANGE",
            "archival_status": "ARCHIVAL_INTEGRATION_COMPLETE_BMSA01_TO_BMSA14_CANONICAL_LINEAGE_VERIFIED",
            "exact_source": {
                "commit": EXACT_SOURCE_COMMIT,
                "sha256": EXPECTED_SOURCE_SHA256,
            },
            "full_project_archive": {
                "file": project_archive.name,
                "sha256": EXPECTED_PROJECT_ARCHIVE_SHA256,
                "project_files": EXPECTED_PROJECT_FILES,
                "inner_zips": EXPECTED_PROJECT_ZIPS,
            },
            "branch_count": 14,
            "canonical_branch_artifact_count": 14,
            "cross_branch_final": {
                "upstream_candidate_count": 15,
                "control_count": 2,
                "registered_case_count": 17,
                "bounded_source_level_residual_gap_candidate_count": 15,
                "candidate_specific_validated_mitigation_count": 0,
                "upstream_classification_changes": 0,
                "residual_weakness_declared_count": 0,
                "residual_risk_declared_count": 0,
                "cross_case_causal_compound_execution_established": False,
                "novelty": "UNDETERMINED",
                "legal_opinion": False,
            },
            "scientific_result_changes_made_by_this_package": 0,
        },
    )

    full_dir = root / "FULL_PROJECT_ARCHIVE"
    copy_with_sidecar(project_archive, full_dir)
    source_dir = root / "EXACT_SOURCE"
    source_dir.mkdir(parents=True)
    shutil.copy2(source_zip, source_dir / source_zip.name)
    write_text(source_dir / f"{source_zip.name}.sha256", f"{EXPECTED_SOURCE_SHA256}  {source_zip.name}\n")

    protocol_sources = [
        project_root / "PHASE_0/BMS_TECHNOLOGY_AUDIT_PHASE0_v0.1.0_STARTER.zip",
        project_root / "指令書/BMS_TECHNOLOGY_AUDIT_FINE_GRAIN_EXECUTION_PROTOCOL_v1.0.0.zip",
    ]
    for source in protocol_sources:
        copy_with_sidecar(source, root / "PROTOCOL")

    canonical_ledger = []
    for branch in BRANCHES:
        source = project_root / branch["directory"] / branch["canonical_artifact"]
        target, target_sidecar = copy_with_sidecar(source, root / "CANONICAL_BRANCH_ARTIFACTS" / branch["branch_id"])
        canonical_ledger.append(
            {
                "branch_id": branch["branch_id"],
                "file": target.relative_to(root).as_posix(),
                "sidecar": target_sidecar.relative_to(root).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": branch["sha256"],
            }
        )
    write_json(root / "CANONICAL_ARTIFACTS_SHA256.json", {"count": 14, "records": canonical_ledger})

    for branch_id, relative in STATUS_REPORT_SOURCES.items():
        source = project_root / relative
        require(source.is_file(), f"status report missing: {relative}")
        destination = root / "STATUS_REPORTS" / f"{branch_id}_STATUS_REPORT.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    bmsa07_reconstruction = project_root / "BMSA-07/PROJECT_STATE_RECONSTRUCTION.json"
    shutil.copy2(bmsa07_reconstruction, root / "LINEAGE_BMSA01_TO_BMSA07_PROJECT_STATE_RECONSTRUCTION.json")
    bmsa14_master = project_root / "BMSA-14/BMSA14_RESIDUAL_GAP_DETERMINATION_MASTER_REFERENCE_PACKAGE_v1.0.2.zip"
    extract_curated_bmsa14(bmsa14_master, root / "CROSS_BRANCH")

    packaging_anomalies = {
        "classification": "PRESERVED_INHERITED_PACKAGING_RECORD_ANOMALIES_NOT_SCIENTIFIC_RESULT_DEFECTS",
        "project_bytes_modified_to_correct_anomalies": 0,
        "all_inner_zip_crc_pass": True,
        "all_inner_zips_have_root_manifest": True,
        "sidecar_anomaly_count": len(sidecar_anomalies),
        "sidecar_anomalies": [
            {
                "path": record["path"],
                "status": record["sidecar"]["status"],
                "declared_sha256": record["sidecar"].get("declared_sha256"),
                "actual_sha256": record["sidecar"].get("actual_sha256"),
                "declared_name": record["sidecar"].get("declared_name"),
            }
            for record in sidecar_anomalies
        ],
        "manifest_anomaly_count": len(manifest_anomalies),
        "manifest_anomalies": [
            {"path": record["path"], "errors": record["manifest_errors"]} for record in manifest_anomalies
        ],
        "canonical_branch_artifacts_affected": 0,
    }
    write_json(root / "INTEGRITY/INHERITED_PACKAGING_ANOMALIES.json", packaging_anomalies)
    write_json(
        root / "INTEGRITY/PROJECT_TREE_SHA256_MANIFEST.json",
        {"root": project_root.name, "file_count": len(tree_records), "files": tree_records},
    )
    write_json(
        root / "INTEGRITY/INNER_ZIP_INTEGRITY_LEDGER.json",
        {
            "zip_count": len(inner_records),
            "crc_pass_count": sum(record["crc_pass"] for record in inner_records),
            "root_manifest_present_count": len(inner_records),
            "manifest_record_pass_count": sum(record["manifest_pass"] for record in inner_records),
            "sidecar_pass_count": sum(record["sidecar"]["status"] == "PASS" for record in inner_records),
            "records": inner_records,
        },
    )
    integrity = {
        "overall_pass": True,
        "project_archive": archive_verification,
        "project_tree": {
            "file_count": len(tree_records),
            "expected_file_count": EXPECTED_PROJECT_FILES,
            "inner_zip_count": len(inner_records),
            "expected_inner_zip_count": EXPECTED_PROJECT_ZIPS,
        },
        "inner_zip_crc": {
            "pass_count": sum(record["crc_pass"] for record in inner_records),
            "failure_count": sum(not record["crc_pass"] for record in inner_records),
        },
        "canonical_artifacts": {"count": len(branch_records), "all_sha_sidecar_crc_pass": True},
        "known_inherited_packaging_anomalies": {
            "sidecar": len(sidecar_anomalies),
            "manifest": len(manifest_anomalies),
            "unexpected": 0,
            "scientific_result_defect": False,
        },
        "scientific_result_changes": 0,
    }
    write_json(root / "INTEGRITY/PROJECT_INTEGRITY_VERIFICATION.json", integrity)

    reproduction_dir = root / "REPRODUCTION"
    reproduction_dir.mkdir(parents=True)
    shutil.copy2(Path(__file__).resolve(), reproduction_dir / Path(__file__).name)
    verifier_source = Path(__file__).with_name("verify_project_master_independent.py")
    require(verifier_source.is_file(), "independent verifier source missing")
    shutil.copy2(verifier_source, reproduction_dir / verifier_source.name)

    manifest_files = file_inventory(root)
    write_json(
        root / "MANIFEST.json",
        {
            "package": MASTER_ROOT,
            "schema_version": "1.0",
            "manifest_excludes_itself": True,
            "file_count_excluding_manifest": len(manifest_files),
            "files": manifest_files,
        },
    )

    output_zip = output_dir / MASTER_ZIP
    deterministic_zip(root, output_zip)
    output_sha = sha256_file(output_zip)
    write_text(output_dir / f"{MASTER_ZIP}.sha256", f"{output_sha}  {MASTER_ZIP}\n")
    shutil.copy2(root / "PROJECT_CLOSURE_SUMMARY.md", output_dir / STATUS_FILE)
    print(
        json.dumps(
            {
                "status": "PASS",
                "master": str(output_zip),
                "master_sha256": output_sha,
                "master_members": len(manifest_files) + 1,
                "project_files": len(tree_records),
                "project_inner_zips": len(inner_records),
                "canonical_artifacts": len(branch_records),
                "known_sidecar_anomalies": len(sidecar_anomalies),
                "known_manifest_anomalies": len(manifest_anomalies),
            },
            indent=2,
        )
    )


def finalize(args: argparse.Namespace) -> None:
    output_dir = args.output_dir.resolve()
    verification = args.independent_verification.resolve()
    require(verification.is_file(), "independent verification missing")
    verification_data = json.loads(verification.read_text(encoding="utf-8"))
    require(verification_data.get("overall_pass") is True, "independent verification failed")
    master = output_dir / MASTER_ZIP
    sidecar = output_dir / f"{MASTER_ZIP}.sha256"
    status = output_dir / STATUS_FILE
    for path in (master, sidecar, status):
        require(path.is_file(), f"delivery file missing: {path.name}")
    target_iv = output_dir / f"{MASTER_ROOT}_INDEPENDENT_VERIFICATION.json"
    if verification != target_iv:
        shutil.copy2(verification, target_iv)
    files = []
    for path in (master, sidecar, status, target_iv):
        files.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(
        output_dir / DELIVERY_MANIFEST,
        {
            "delivery": "BMS Technology Audit Master of All v1.0.0",
            "overall_pass": True,
            "archival_status": "ARCHIVAL_INTEGRATION_COMPLETE_BMSA01_TO_BMSA14_CANONICAL_LINEAGE_VERIFIED",
            "file_count_excluding_this_manifest": len(files),
            "files": files,
            "master_sha256": sha256_file(master),
            "independent_verification_pass": True,
        },
    )
    print(json.dumps({"status": "PASS", "delivery_manifest": str(output_dir / DELIVERY_MANIFEST)}, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--project-tree", type=Path, required=True)
    build_parser.add_argument("--project-archive", type=Path, required=True)
    build_parser.add_argument("--source-zip", type=Path, required=True)
    build_parser.add_argument("--work-dir", type=Path, required=True)
    build_parser.add_argument("--output-dir", type=Path, required=True)
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--output-dir", type=Path, required=True)
    finalize_parser.add_argument("--independent-verification", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "build":
        build(args)
    else:
        finalize(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise
