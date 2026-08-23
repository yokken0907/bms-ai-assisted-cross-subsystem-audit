#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

PUB_FILE = 'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.zip'
PUB_SHA = '5f783e651f3e64e2063a28c9bfc9337d7978f4421eee738290d01fa58fe47279'
PUBLICATION_SET_ROOT = 'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1/'

MASTER_FILE = 'BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip'
MASTER_SHA = '4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7'

DOCS = {
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_MAIN_MANUSCRIPT_v1.1.docx':
        'ff872a2ddd6c039786232631525d7c53622442f18ab2346c11c1ad1698b9484a',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_A_v1.1.docx':
        'f4d086a92c77094867559516ce7635687f1e742c5f0f14cc90cc662ab31f8145',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_B_v1.1.docx':
        '02cc9a657d79eb8c25cc7e8bf1b0a29687339c32c5102fb1f5ee8d457a7552c2',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_C_v1.1.docx':
        'f138cecd5c75aef215bcb5c7b6b08b872206b790b1fe81c876a6f86751132a0c',
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--publication-set', type=Path, required=True)
    ap.add_argument('--master-of-all', type=Path, required=True)
    args = ap.parse_args()

    errors: list[str] = []
    report: dict[str, object] = {}

    for label, path, expected in (
        ('publication_set', args.publication_set, PUB_SHA),
        ('master_of_all', args.master_of_all, MASTER_SHA),
    ):
        actual = sha256_file(path)
        passed = actual == expected
        report[label] = {
            'file': path.name,
            'expected_sha256': expected,
            'actual_sha256': actual,
            'pass': passed,
        }
        if not passed:
            errors.append(label + ' SHA mismatch')

    try:
        with zipfile.ZipFile(args.publication_set) as z:
            names = z.namelist()
            name_set = set(names)

            root_present = PUBLICATION_SET_ROOT in name_set
            report['publication_canonical_root'] = {
                'root': PUBLICATION_SET_ROOT,
                'directory_entry_present': root_present,
                'pass': root_present,
            }
            if not root_present:
                errors.append('publication canonical root missing ' + PUBLICATION_SET_ROOT)

            inner: dict[str, object] = {}
            for name, expected_hash in DOCS.items():
                canonical_member = PUBLICATION_SET_ROOT + name
                basename_matches = [
                    member for member in names
                    if not member.endswith('/') and PurePosixPath(member).name == name
                ]

                location_unique = basename_matches == [canonical_member]
                if not location_unique:
                    errors.append(
                        'publication member location/uniqueness mismatch '
                        + name
                        + ': '
                        + json.dumps(basename_matches)
                    )

                if canonical_member not in name_set:
                    errors.append('publication set missing ' + canonical_member)
                    inner[name] = {
                        'canonical_member': canonical_member,
                        'basename_matches': basename_matches,
                        'canonical_presence': False,
                        'location_unique': location_unique,
                        'pass': False,
                    }
                    continue

                zip_hash = sha256_bytes(z.read(canonical_member))
                repo_path = ROOT / 'paper' / name
                if not repo_path.is_file():
                    errors.append('repository paper missing ' + name)
                    inner[name] = {
                        'canonical_member': canonical_member,
                        'basename_matches': basename_matches,
                        'canonical_presence': True,
                        'location_unique': location_unique,
                        'zip_sha256': zip_hash,
                        'expected_sha256': expected_hash,
                        'repo_paper_present': False,
                        'pass': False,
                    }
                    continue

                repo_hash = sha256_file(repo_path)
                identity_ok = zip_hash == expected_hash == repo_hash
                passed = location_unique and identity_ok
                inner[name] = {
                    'canonical_member': canonical_member,
                    'basename_matches': basename_matches,
                    'canonical_presence': True,
                    'location_unique': location_unique,
                    'zip_sha256': zip_hash,
                    'repo_paper_sha256': repo_hash,
                    'expected_sha256': expected_hash,
                    'pass': passed,
                }
                if not identity_ok:
                    errors.append('paper identity mismatch ' + name)

            report['publication_docx_identity'] = inner

    except zipfile.BadZipFile:
        errors.append('publication set bad ZIP')

    report['pass'] = not errors
    report['errors'] = errors
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
