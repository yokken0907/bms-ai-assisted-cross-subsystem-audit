#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SOURCE_SHA="2cf5cfa7c12aa27b41795650695898abd0bce79af746b8e6ca8dd0c5368c1fa2"; COMMIT="308028fb13d046ba29b98886895c2e17937b1437"
def run(cmd):
 p=subprocess.run(cmd,text=True);
 if p.returncode: raise SystemExit(p.returncode)
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument('--source-zip',type=Path); ap.add_argument('--fetch-source',action='store_true'); ap.add_argument('--strict',action='store_true'); a=ap.parse_args()
run([sys.executable,str(ROOT/'scripts/verify_repository.py')]); run([sys.executable,str(ROOT/'scripts/verify_paper_hashes.py')]); run([sys.executable,str(ROOT/'scripts/verify_witness_hashes.py')]); run([sys.executable,str(ROOT/'scripts/verify_publication_invariants.py')])
source=a.source_zip
if a.fetch_source:
 p=subprocess.run([sys.executable,str(ROOT/'scripts/fetch_exact_source.py')],text=True,capture_output=True); print(p.stdout,end='');
 if p.returncode: print(p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
 source=Path(p.stdout.splitlines()[0].strip())
if source is None:
 msg={'status':'PARTIAL_PASS','source_dependent_checks':'SKIPPED','instruction':'provide --source-zip or --fetch-source'}; print(json.dumps(msg,indent=2)); raise SystemExit(1 if a.strict else 0)
if sha(source)!=SOURCE_SHA: raise SystemExit('source ZIP SHA mismatch')
run([sys.executable,str(ROOT/'scripts/verify_source_anchors.py'),str(source)])
with tempfile.TemporaryDirectory(prefix='bms-source-') as td:
 td=Path(td);
 with zipfile.ZipFile(source) as z: z.extractall(td)
 roots=[x for x in td.iterdir() if x.is_dir()];
 if len(roots)!=1: raise SystemExit('unexpected source layout')
 run([sys.executable,str(ROOT/'scripts/run_witnesses.py'),'--source',str(roots[0])])
print(json.dumps({'status':'FULL_PASS','source_sha256':SOURCE_SHA,'candidate_count':15,'control_count':2,'source_anchor_count':25,'paper_files':'OPTIONAL_PREPUBLICATION'},indent=2))
