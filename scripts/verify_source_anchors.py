#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA="2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2"
COMMIT="308028fb13d046ba29b98886895c2e17937b1437"

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def git_blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode('ascii')+b"\0"+b).hexdigest()
def sha_file(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

p=argparse.ArgumentParser(); p.add_argument('source_zip',type=Path); a=p.parse_args()
if sha_file(a.source_zip)!=EXPECTED_SOURCE_SHA: raise SystemExit('exact source ZIP SHA-256 mismatch')
rows=json.loads((ROOT/'data/source_anchors_25.json').read_text())
errors=[]
with zipfile.ZipFile(a.source_zip) as z:
 prefix=f'foxbms-2-{COMMIT}/'
 names=set(z.namelist())
 for r in rows:
  member=prefix+r['path']
  if member not in names: errors.append(f"missing source file: {r['case_id']} {r['path']}"); continue
  b=z.read(member)
  if sha256_bytes(b)!=r['source_file_sha256']: errors.append(f"file sha mismatch: {r['case_id']} {r['path']}")
  if git_blob(b)!=r['source_file_git_blob_sha1']: errors.append(f"git blob mismatch: {r['case_id']} {r['path']}")
  t=b.decode('utf-8',errors='replace'); lines=t.splitlines()
  if r['marker'] not in t: errors.append(f"marker absent: {r['case_id']} {r['marker']}")
  lo=max(0,int(r['first_line'])-1); hi=min(len(lines),int(r['last_line']))
  if not any(r['marker'] in line for line in lines[lo:hi]): errors.append(f"marker not in frozen line range: {r['case_id']} {r['path']}")
print(json.dumps({'pass':not errors,'case_count':len(set(r['case_id'] for r in rows)),'anchor_count':len(rows),'errors':errors},indent=2))
raise SystemExit(0 if not errors else 1)
