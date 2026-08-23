#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
expected={}
for line in (ROOT/'paper/SHA256SUMS_v1.1.txt').read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    h,n=line.split(maxsplit=1); expected[n.strip().lstrip('*')]=h
errors=[]
for name,h in expected.items():
    p=ROOT/'paper'/name
    if not p.is_file(): errors.append(f'missing {name}'); continue
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=h: errors.append(f'hash mismatch {name}: {actual}')
print({'pass':not errors,'checked':len(expected),'errors':errors})
raise SystemExit(0 if not errors else 1)
