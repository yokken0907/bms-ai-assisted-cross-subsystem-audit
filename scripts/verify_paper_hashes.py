#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
ap=argparse.ArgumentParser(description='Verify externally supplied Version 1.1.1 publication files against the canonical final binding. Manuscript files are intentionally not stored in this GitHub repository.')
ap.add_argument('--paper-dir',type=Path,required=True)
a=ap.parse_args()
binding=json.loads((ROOT/'release/FINAL_RELEASE_BINDING_v1.1.1.json').read_text(encoding='utf-8'))
expected=binding.get('paper_artifact_hashes',{})
errors=[]
for name,h in expected.items():
    p=a.paper_dir/name
    if not p.is_file(): errors.append(f'missing {name}'); continue
    actual=sha(p)
    if actual!=h: errors.append(f'hash mismatch {name}: {actual}')
print(json.dumps({'pass':not errors,'checked':len(expected),'paper_dir':str(a.paper_dir),'repository_contains_papers':False,'errors':errors},indent=2))
raise SystemExit(0 if not errors else 1)
