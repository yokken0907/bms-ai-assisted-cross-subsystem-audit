#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUB_FILE='BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.1.zip'
PUB_ROOT='BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_PUBLICATION_SET_v1.1.1/'
MASTER_FILE='BMS_TECHNOLOGY_AUDIT_MASTER_OF_ALL_v1.0.0.zip'
DOCS=[
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_MAIN_MANUSCRIPT_v1.1.1.docx',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_MAIN_MANUSCRIPT_v1.1.1.pdf',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_A_v1.1.1.docx',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_A_v1.1.1.pdf',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_B_v1.1.1.docx',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_B_v1.1.1.pdf',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_C_v1.1.1.docx',
'BMS_AI_ASSISTED_CROSS_SUBSYSTEM_AUDIT_SUPPLEMENT_C_v1.1.1.pdf']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description='Verify external publication/Master assets against the GitHub repository binding. The assets themselves are intentionally not stored here.')
 ap.add_argument('--publication-set',type=Path,required=True); ap.add_argument('--master-of-all',type=Path,required=True); a=ap.parse_args()
 errors=[]; report={'repository_distribution':'github-reproducibility-only'}
 binding_path=ROOT/'release/FINAL_RELEASE_BINDING_v1.1.1.json'; manifest_path=ROOT/'release/RELEASE_ASSET_MANIFEST.json'
 binding=json.loads(binding_path.read_text(encoding='utf-8')); manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 if not a.publication_set.is_file(): errors.append('publication set missing')
 if not a.master_of_all.is_file(): errors.append('master missing')
 if errors:
  print(json.dumps({'pass':False,'errors':errors},indent=2)); return 1
 actual_pub=sha(a.publication_set); exp_pub=binding['publication_set']['sha256']
 actual_master=sha(a.master_of_all); exp_master=binding['master_of_all']['sha256']
 report['publication_set']={'actual_sha256':actual_pub,'expected_sha256':exp_pub,'pass':actual_pub==exp_pub,'stored_in_github':False}
 report['master_of_all']={'actual_sha256':actual_master,'expected_sha256':exp_master,'pass':actual_master==exp_master,'stored_in_github':False}
 if actual_pub!=exp_pub: errors.append('publication set SHA mismatch')
 if actual_master!=exp_master: errors.append('master SHA mismatch')
 expected_papers=binding.get('paper_artifact_hashes',{})
 try:
  with zipfile.ZipFile(a.publication_set) as z:
   names=set(z.namelist())
   expected_members={PUB_ROOT+'paper/'+n for n in DOCS}|{PUB_ROOT+'PUBLICATION_MANIFEST.json',PUB_ROOT+'SHA256SUMS.txt',PUB_ROOT+'PROVENANCE.json',PUB_ROOT+'RELEASE_NOTES.md'}
   for m in sorted(expected_members-names): errors.append('publication set missing '+m)
   for name,h in expected_papers.items():
    member=PUB_ROOT+'paper/'+name
    if member in names and hashlib.sha256(z.read(member)).hexdigest()!=h: errors.append('publication artifact hash mismatch '+name)
 except zipfile.BadZipFile: errors.append('publication set bad ZIP')
 if manifest.get('publication_set_sha256')!=actual_pub: errors.append('release manifest publication set mismatch')
 if manifest.get('master_of_all_sha256')!=actual_master: errors.append('release manifest master mismatch')
 if manifest.get('final_release_binding_sha256')!=sha(binding_path): errors.append('release manifest final binding hash mismatch')
 report['final_binding']={'file':str(binding_path),'sha256':sha(binding_path)}
 report['pass']=not errors; report['errors']=errors; print(json.dumps(report,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
