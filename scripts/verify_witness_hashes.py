#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data/candidate_witnesses_15.json').read_text())
errors=[]
for r in rows:
 p=ROOT/'witnesses'/r['file']
 if not p.is_file(): errors.append(f"missing {r['file']}"); continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=r['sha256']: errors.append(f"hash mismatch {r['case_id']} {r['file']}")
# Controls are verified against the frozen 17-case register stored locally.
case17=json.loads((ROOT/'data/case_register_17.json').read_text())
for r in case17:
 if r['role']!='CONTROL': continue
 p=ROOT/'witnesses'/r['witness_file']; h=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
 if h!=r['witness_sha256']: errors.append(f"control hash mismatch {r['case_id']}")
print({'pass':not errors,'candidate_witnesses':len(rows),'controls':2,'errors':errors})
raise SystemExit(0 if not errors else 1)
