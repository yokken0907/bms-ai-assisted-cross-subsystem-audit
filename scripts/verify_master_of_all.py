#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; EXPECTED="4cb220a0a7331062becb25240e28b330a02f258a21d44050cdba40ffdcd4efc7"; MASTER_ROOT='BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0'
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
ap=argparse.ArgumentParser(); ap.add_argument('master_zip',type=Path); ap.add_argument('--output',type=Path,default=Path('results/master_verification_22_gates.json')); a=ap.parse_args()
if sha(a.master_zip)!=EXPECTED: raise SystemExit('Master-of-All SHA-256 mismatch')
with tempfile.TemporaryDirectory(prefix='bms-master-') as td:
 td=Path(td); canonical=td/(MASTER_ROOT+'.zip'); shutil.copy2(a.master_zip,canonical); (td/(MASTER_ROOT+'.zip.sha256')).write_text(EXPECTED+'  '+canonical.name+'\n')
 with zipfile.ZipFile(canonical) as z:
  project=td/'BMS_TECHNOLOGY_AUDIT(18).zip'; project.write_bytes(z.read(MASTER_ROOT+'/FULL_PROJECT_ARCHIVE/BMS_TECHNOLOGY_AUDIT(18).zip'))
  source=td/'foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip'; source.write_bytes(z.read(MASTER_ROOT+'/EXACT_SOURCE/foxbms-2_308028fb13d046ba29b98886895c2e17937b1437.zip'))
 tree_parent=td/'tree'; tree_parent.mkdir();
 with zipfile.ZipFile(project) as z: z.extractall(tree_parent)
 roots=[x for x in tree_parent.iterdir() if x.is_dir()];
 if len(roots)!=1: raise SystemExit('unexpected full-project archive layout')
 tempout=td/'result.json'; verifier=ROOT/'scripts/frozen/verify_project_master_independent.py'; cmd=[sys.executable,str(verifier),'--master-zip',str(canonical),'--project-tree',str(roots[0]),'--project-archive',str(project),'--source-zip',str(source),'--output',str(tempout)]; p=subprocess.run(cmd,text=True,capture_output=True); print(p.stdout,end='');
 if p.returncode!=0: print(p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
 result=json.loads(tempout.read_text()); out=ROOT/a.output if not a.output.is_absolute() else a.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');
 if not result['overall_pass'] or len(result['gates'])!=22: raise SystemExit('22-gate verification failed')
 print(json.dumps({'pass':True,'gates_passed':22,'output':str(out)},indent=2))
