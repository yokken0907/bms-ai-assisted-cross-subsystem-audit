#!/usr/bin/env python3
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / 'paper'
EXPECTED = {
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_MAIN_MANUSCRIPT_v1.1.docx': 'ff872a2ddd6c039786232631525d7c53622442f18ab2346c11c1ad1698b9484a',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_A_v1.1.docx': 'f4d086a92c77094867559516ce7635687f1e742c5f0f14cc90cc662ab31f8145',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_B_v1.1.docx': '02cc9a657d79eb8c25cc7e8bf1b0a29687339c32c5102fb1f5ee8d457a7552c2',
    'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_C_v1.1.docx': 'f138cecd5c75aef215bcb5c7b6b08b872206b790b1fe81c876a6f86751132a0c',
}

# Pre-publication public-tree mode: the manuscript files are intentionally absent.
# If paper/ is absent, report a successful optional skip. If paper/ exists, require
# the complete canonical set and verify every byte identity.
if not PAPER_DIR.exists():
    print(json.dumps({
        'pass': True,
        'status': 'SKIPPED_OPTIONAL_PAPER_FILES',
        'reason': 'paper/ intentionally absent from pre-publication public Git tree',
        'canonical_paper_count': len(EXPECTED),
    }, indent=2))
    raise SystemExit(0)

errors = []
for name, expected_hash in EXPECTED.items():
    p = PAPER_DIR / name
    if not p.is_file():
        errors.append(f'missing {name}')
        continue
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected_hash:
        errors.append(f'hash mismatch {name}: {actual}')

unexpected_docx = sorted(
    p.name for p in PAPER_DIR.glob('*.docx') if p.name not in EXPECTED
)
if unexpected_docx:
    errors.append('unexpected DOCX files: ' + ', '.join(unexpected_docx))

print(json.dumps({
    'pass': not errors,
    'status': 'PASS' if not errors else 'FAIL',
    'checked': len(EXPECTED),
    'errors': errors,
}, indent=2))
raise SystemExit(0 if not errors else 1)
