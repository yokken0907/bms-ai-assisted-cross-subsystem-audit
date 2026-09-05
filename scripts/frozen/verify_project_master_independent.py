#!/usr/bin/env python3
"""Independent verifier for the BMSA-01..14 Master-of-All package."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = "BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0"
MASTER_NAME = f"{ROOT}.zip"
PROJECT_SHA = "b21d2e5078ddb95eb692c569e1f327b4d609ba72c99f34552d923448fa36479d"
SOURCE_SHA = "2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2"
SOURCE_COMMIT = "308028fb13d046ba29b98886895c2e17937b1437"
PROJECT_FILES = 810
PROJECT_ZIPS = 383
FINAL_DISPOSITION = "PERSISTS_AS_BOUNDED_SOURCE_LEVEL_RESIDUAL_GAP_CANDIDATE"


CANONICAL = {
    "BMSA-01": ("BMS_TECHNOLOGY_AUDIT_BMSA01_PHASE5_v0.6.2_AUDITED_CLOSEOUT.zip", "9a0cd9663859687d8947cece1acf3967bdaa91db071cffc4ccb75c12557fc48e"),
    "BMSA-02": ("BMSA02_STATE_ESTIMATION_MASTER_REFERENCE_PACKAGE_v1.0.0.zip", "d1257fdde252f8d768b0b9de99248ad2b9f726ffd6508d26fe2dc8ffb58f9982"),
    "BMSA-03": ("BMSA03_OPERATING_LIMITS_MASTER_REFERENCE_PACKAGE_v1.0.0.zip", "7aee6428f03082d44d8dfb393945aff06ba5c84c507cf3eb2716bb3313008e3d"),
    "BMSA-04": ("BMS_TECHNOLOGY_AUDIT_BMSA04_v1.6.2_AUDITED_CLOSEOUT.zip", "234f9d2ead593801db5cdce943b658e5f0b63daa149be1af0da348a58bc94fb4"),
    "BMSA-05": ("BMS_TECHNOLOGY_AUDIT_BMSA05_FINAL_CLOSURE_v1.2.0.zip", "b8bba89ca9f88bc0a6d2d8ae687c5494587ea76692b76b23478e5d1b9aca7b8a"),
    "BMSA-06": ("BMS_TECHNOLOGY_AUDIT_BMSA06_PHASE5_v0.6.6_AUDITED_CLOSEOUT.zip", "35695fb5e7d3a7cf1f7655c565b0ae279860246c51c9b026ba5f97fe1ac175c0"),
    "BMSA-07": ("BMSA07_FAULT_DIAGNOSIS_MASTER_REFERENCE_PACKAGE_v1.0.2.zip", "7bd657017e159d9a3355643b51c9ee688f25f67de66b3892fcc13a52661c238c"),
    "BMSA-08": ("BMSA08_SUPERVISORY_STATE_MACHINE_MASTER_REFERENCE_PACKAGE_v1.0.2.zip", "2a0d3ffe60678a93fda9b78adea01fcb59f9352b3fa886ec7a3415264057632e"),
    "BMSA-09": ("BMSA09_COMMUNICATIONS_DISTRIBUTED_BMS_MASTER_REFERENCE_PACKAGE_v1.0.2.zip", "24bc35d3c6c0d412751c8d55c625887f796f34751ec78e38966971185879221d"),
    "BMSA-10": ("BMSA10_SOFTWARE_ASSURANCE_MASTER_REFERENCE_PACKAGE_v1.0.3.zip", "c12bf680baf458b705783a664f96ac7afc5decb87b3596d7a89c69775daa9d7f"),
    "BMSA-11": ("BMSA11_AGING_PARAMETER_ADAPTATION_MASTER_REFERENCE_PACKAGE_v1.0.2.zip", "590a983de6f823ae337fb86ce5c1cf37bbeb82bfa13370be75379aae24b70f64"),
    "BMSA-12": ("BMSA12_UNIFIED_REPRODUCTION_STRESS_HARNESS_MASTER_REFERENCE_PACKAGE_v1.0.3.zip", "d8000ef499b29af4ffcf71e23abd2a93a504bac25d6f19babe2d7d06437efed3"),
    "BMSA-13": ("BMSA13_EXISTING_MITIGATION_PATENT_MAP_MASTER_REFERENCE_PACKAGE_v1.0.3.zip", "4fd5e1a1dc7204cb7834306d78c06c320668bc062ea0f20d6e3baa8604160097"),
    "BMSA-14": ("BMSA14_RESIDUAL_GAP_DETERMINATION_MASTER_REFERENCE_PACKAGE_v1.0.2.zip", "8156c9227fa64c82b9589e480fdcd3ba760ee46271fac5baa19f6dab0aff3dce"),
}


SIDE_ANOMALIES = {
    "BMSA-04/BMS_TECHNOLOGY_AUDIT_BMSA04_HISTORY_SOC_PHASE2C_v0.5.0_RESULTS_FOR_REVIEW.zip",
    "BMSA-04/BMS_TECHNOLOGY_AUDIT_BMSA04_HISTORY_SOC_PHASE2D_v0.6.0_RESULTS_FOR_REVIEW.zip",
    "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_v0.4.2_CORRECTED_CLOSEOUT_RESULTS_FOR_REVIEW.zip",
    "BMSA-06/BMS_TECHNOLOGY_AUDIT_BMSA06_PHASE5_v0.6.4_RUN02R_EXACT_ACQUISITION_BRIDGE_STARTER (1).zip",
}

MANIFEST_ANOMALIES = {
    "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_REFERENCE_AUDIT_v0.4.1_STARTER.zip",
    "BMSA_02/BMS_TECHNOLOGY_AUDIT_BMSA02_PHASE2A_v0.4.2_CORRECTED_CLOSEOUT_RESULTS_FOR_REVIEW.zip",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            records[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
    return records


def sidecar_status(path: Path) -> str:
    sidecar = path.with_name(path.name + ".sha256")
    if not sidecar.is_file():
        return "MISSING"
    fields = sidecar.read_text(encoding="utf-8", errors="replace").strip().split(maxsplit=1)
    if not fields or fields[0] != sha256_file(path):
        return "HASH_MISMATCH"
    if len(fields) < 2 or fields[1].strip() != path.name:
        return "NAME_ANOMALY_HASH_MATCH"
    return "PASS"


def root_manifest(names: list[str]) -> str | None:
    candidates = [name for name in names if name == "MANIFEST.json" or name.endswith("/MANIFEST.json")]
    return min(candidates, key=lambda value: value.count("/")) if candidates else None


def inspect_tree_zip(path: Path, root: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            names = [name for name in archive.namelist() if not name.endswith("/")]
            manifest_name = root_manifest(names)
            if manifest_name is None:
                errors.append("manifest_missing")
            else:
                prefix = manifest_name[: -len("MANIFEST.json")]
                manifest = json.loads(archive.read(manifest_name))
                expected = {manifest_name}
                for record in manifest.get("files", []):
                    member = prefix + record["path"]
                    expected.add(member)
                    if member not in names:
                        errors.append(f"missing:{member}")
                        continue
                    data = archive.read(member)
                    if len(data) != record["bytes"] or sha256_bytes(data) != record["sha256"]:
                        errors.append(f"mismatch:{member}")
                errors.extend(f"unmanifested:{name}" for name in sorted(set(names) - expected))
    except Exception as exc:
        return {"path": path.relative_to(root).as_posix(), "crc_pass": False, "manifest_errors": [str(exc)], "sidecar": sidecar_status(path)}
    return {
        "path": path.relative_to(root).as_posix(),
        "crc_pass": bad is None,
        "manifest_errors": errors,
        "sidecar": sidecar_status(path),
    }


def verify_outer(path: Path, tree: Path, tree_inventory: dict[str, dict[str, Any]]) -> bool:
    if sha256_file(path) != PROJECT_SHA:
        return False
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            return False
        names = {name for name in archive.namelist() if not name.endswith("/")}
        expected = {f"{tree.name}/{relative}" for relative in tree_inventory}
        if names != expected:
            return False
        for relative, record in tree_inventory.items():
            data = archive.read(f"{tree.name}/{relative}")
            if len(data) != record["bytes"] or sha256_bytes(data) != record["sha256"]:
                return False
    return True


def verify_master_manifest(archive: zipfile.ZipFile) -> tuple[bool, dict[str, Any], set[str], list[str]]:
    errors: list[str] = []
    members = {name for name in archive.namelist() if not name.endswith("/")}
    manifest_name = f"{ROOT}/MANIFEST.json"
    if manifest_name not in members:
        return False, {}, members, ["manifest_missing"]
    manifest = json.loads(archive.read(manifest_name))
    expected = {manifest_name}
    for record in manifest.get("files", []):
        member = f"{ROOT}/{record['path']}"
        expected.add(member)
        if member not in members:
            errors.append(f"missing:{member}")
            continue
        data = archive.read(member)
        if len(data) != record["bytes"] or sha256_bytes(data) != record["sha256"]:
            errors.append(f"mismatch:{member}")
    errors.extend(f"unmanifested:{name}" for name in sorted(members - expected))
    return not errors, manifest, members, errors


def nested_json(zip_bytes: bytes, basename: str) -> Any:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        root = min(name.split("/", 1)[0] for name in names if not name.endswith("/"))
        return json.loads(archive.read(f"{root}/{basename}"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-zip", type=Path, required=True)
    parser.add_argument("--project-tree", type=Path, required=True)
    parser.add_argument("--project-archive", type=Path, required=True)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    master = args.master_zip.resolve()
    tree = args.project_tree.resolve()
    project_archive = args.project_archive.resolve()
    source_zip = args.source_zip.resolve()
    tree_inv = inventory(tree)
    tree_zips = sorted(tree.rglob("*.zip"))
    tree_zip_records = [inspect_tree_zip(path, tree) for path in tree_zips]
    side_anomaly_set = {record["path"] for record in tree_zip_records if record["sidecar"] != "PASS"}
    manifest_anomaly_set = {record["path"] for record in tree_zip_records if record["manifest_errors"]}

    with zipfile.ZipFile(master) as archive:
        master_crc = archive.testzip()
        manifest_pass, manifest, members, manifest_errors = verify_master_manifest(archive)
        read_json = lambda relative: json.loads(archive.read(f"{ROOT}/{relative}"))
        index = read_json("PROJECT_MASTER_INDEX.json")
        source_identity = read_json("EXACT_SOURCE_IDENTITY.json")
        branch_ledger = read_json("BRANCH_CLOSURE_LEDGER.json")
        anomaly_ledger = read_json("INTEGRITY/INHERITED_PACKAGING_ANOMALIES.json")
        zip_ledger = read_json("INTEGRITY/INNER_ZIP_INTEGRITY_LEDGER.json")
        candidate_determinations = read_json("CROSS_BRANCH/RESIDUAL_GAP_DETERMINATIONS_15_CASES.json")
        cross_ledger = read_json("CROSS_BRANCH/CROSS_CASE_LEDGER_15_CASES.json")
        embedded_outer = archive.read(f"{ROOT}/FULL_PROJECT_ARCHIVE/{project_archive.name}")
        embedded_source = archive.read(f"{ROOT}/EXACT_SOURCE/{source_zip.name}")
        embedded_canonical = {}
        canonical_crc_pass = True
        for branch_id, (filename, expected_sha) in CANONICAL.items():
            member = f"{ROOT}/CANONICAL_BRANCH_ARTIFACTS/{branch_id}/{filename}"
            data = archive.read(member)
            embedded_canonical[branch_id] = sha256_bytes(data) == expected_sha
            with zipfile.ZipFile(io.BytesIO(data)) as nested:
                canonical_crc_pass = canonical_crc_pass and nested.testzip() is None
        bmsa14_name = CANONICAL["BMSA-14"][0]
        bmsa14_bytes = archive.read(f"{ROOT}/CANONICAL_BRANCH_ARTIFACTS/BMSA-14/{bmsa14_name}")
        bmsa14_final = nested_json(bmsa14_bytes, "FINAL_FINDINGS.json")

    sidecar_ok = False
    sidecar = master.with_name(master.name + ".sha256")
    if sidecar.is_file():
        fields = sidecar.read_text(encoding="utf-8").strip().split(maxsplit=1)
        sidecar_ok = len(fields) == 2 and fields[0] == sha256_file(master) and fields[1].strip() == master.name

    branch_rows = {record["branch_id"]: record for record in branch_ledger.get("records", [])}
    branches_ok = set(branch_rows) == set(CANONICAL)
    if branches_ok:
        for branch_id, (filename, expected_sha) in CANONICAL.items():
            row = branch_rows[branch_id]
            branches_ok = branches_ok and row["canonical_artifact"] == filename and row["sha256"] == expected_sha

    candidate_ids = {record["case_id"] for record in candidate_determinations}
    candidate_rows_ok = (
        len(candidate_determinations) == 15
        and len(candidate_ids) == 15
        and all(record["final_disposition"] == FINAL_DISPOSITION for record in candidate_determinations)
        and all(record["classification_preserved"] is True for record in candidate_determinations)
        and all(record["residual_risk_declared"] is False for record in candidate_determinations)
        and all(record["residual_weakness_declared"] is False for record in candidate_determinations)
        and all(record["product_or_safety_conclusion"] is False for record in candidate_determinations)
    )

    gates = {
        "G01_master_sidecar_sha256_pass": sidecar_ok,
        "G02_master_zip_crc_pass": master_crc is None,
        "G03_master_manifest_exact_member_hash_pass": manifest_pass,
        "G04_exact_source_identity_pass": (
            sha256_file(source_zip) == SOURCE_SHA
            and sha256_bytes(embedded_source) == SOURCE_SHA
            and source_identity["commit"] == SOURCE_COMMIT
            and source_identity["source_zip_sha256"] == SOURCE_SHA
        ),
        "G05_full_project_archive_frozen_sha_pass": sha256_file(project_archive) == PROJECT_SHA and sha256_bytes(embedded_outer) == PROJECT_SHA,
        "G06_project_archive_exact_tree_equality_pass": verify_outer(project_archive, tree, tree_inv),
        "G07_project_tree_count_810_pass": len(tree_inv) == PROJECT_FILES,
        "G08_project_inner_zip_count_383_pass": len(tree_zips) == PROJECT_ZIPS,
        "G09_all_383_inner_zip_crc_pass": len(tree_zip_records) == PROJECT_ZIPS and all(record["crc_pass"] for record in tree_zip_records),
        "G10_known_sidecar_anomaly_set_exact_no_hash_mismatch": (
            side_anomaly_set == SIDE_ANOMALIES
            and all(record["sidecar"] != "HASH_MISMATCH" for record in tree_zip_records)
        ),
        "G11_known_manifest_anomaly_set_exact": manifest_anomaly_set == MANIFEST_ANOMALIES,
        "G12_master_anomaly_ledger_matches_independent_scan": (
            anomaly_ledger["sidecar_anomaly_count"] == 4
            and anomaly_ledger["manifest_anomaly_count"] == 2
            and anomaly_ledger["canonical_branch_artifacts_affected"] == 0
            and anomaly_ledger["project_bytes_modified_to_correct_anomalies"] == 0
        ),
        "G13_all_14_canonical_artifact_sha_pass": len(embedded_canonical) == 14 and all(embedded_canonical.values()),
        "G14_all_14_canonical_artifact_crc_pass": canonical_crc_pass,
        "G15_branch_ledger_14_exact_ids_names_hashes_pass": branches_ok,
        "G16_amended_canonical_versions_selected": (
            branch_rows.get("BMSA-10", {}).get("canonical_artifact", "").endswith("v1.0.3.zip")
            and branch_rows.get("BMSA-12", {}).get("canonical_artifact", "").endswith("v1.0.3.zip")
            and branch_rows.get("BMSA-13", {}).get("canonical_artifact", "").endswith("v1.0.3.zip")
        ),
        "G17_15_bounded_residual_gap_dispositions_preserved": candidate_rows_ok,
        "G18_bmsa14_final_counts_and_claim_boundary_preserved": (
            bmsa14_final["closure_status"] == "BMSA14_CLOSED"
            and bmsa14_final["candidate_count"] == 15
            and bmsa14_final["bounded_residual_gap_candidate_count"] == 15
            and bmsa14_final["classification_changes"] == 0
            and bmsa14_final["candidate_specific_effective_mitigations_validated"] == 0
            and bmsa14_final["residual_weakness_declared_count"] == 0
            and bmsa14_final["residual_risk_declared_count"] == 0
            and bmsa14_final["cross_case_causal_compound_execution_established"] is False
            and bmsa14_final["legal_opinion"] is False
            and bmsa14_final["novelty_status"] == "NOVELTY_UNDETERMINED"
        ),
        "G19_cross_case_ledger_counts_preserved": (
            cross_ledger["candidate_count"] == 15
            and cross_ledger["bounded_residual_gap_candidate_count"] == 15
            and cross_ledger["classification_change_count"] == 0
            and cross_ledger["compound_execution_established"] is False
        ),
        "G20_project_master_index_no_scientific_result_change": (
            index["branch_count"] == 14
            and index["canonical_branch_artifact_count"] == 14
            and index["scientific_result_changes_made_by_this_package"] == 0
            and index["cross_branch_final"]["residual_weakness_declared_count"] == 0
            and index["cross_branch_final"]["residual_risk_declared_count"] == 0
            and index["cross_branch_final"]["legal_opinion"] is False
        ),
        "G21_embedded_inner_zip_ledger_count_pass": (
            zip_ledger["zip_count"] == PROJECT_ZIPS
            and zip_ledger["crc_pass_count"] == PROJECT_ZIPS
            and len(zip_ledger["records"]) == PROJECT_ZIPS
        ),
        "G22_required_reproduction_and_claim_files_present": all(
            f"{ROOT}/{relative}" in members
            for relative in [
                "CLAIM_BOUNDARY.md",
                "PROJECT_CLOSURE_SUMMARY.md",
                "REPRODUCTION/build_project_master.py",
                "REPRODUCTION/verify_project_master_independent.py",
                "CROSS_BRANCH/SOURCE_ANCHOR_VERIFICATION_15_CASES.json",
                "CROSS_BRANCH/WITNESS_SHA256_LINEAGE_15_CASES.json",
            ]
        ),
    }
    overall = all(gates.values())
    result = {
        "overall_pass": overall,
        "verifier": "independent implementation; does not import the builder",
        "master": {
            "file": master.name,
            "bytes": master.stat().st_size,
            "sha256": sha256_file(master),
            "member_count": len(members),
            "manifest_record_count": len(manifest.get("files", [])),
            "manifest_errors": manifest_errors,
        },
        "project": {
            "file_count": len(tree_inv),
            "inner_zip_count": len(tree_zips),
            "sidecar_anomalies": sorted(side_anomaly_set),
            "manifest_anomalies": sorted(manifest_anomaly_set),
        },
        "canonical_artifact_hashes": embedded_canonical,
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"overall_pass": overall, "output": str(args.output), "failed_gates": result["failed_gates"]}, indent=2))
    if not overall:
        raise RuntimeError("independent verification failed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise
