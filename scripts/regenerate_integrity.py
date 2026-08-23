#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def tracked(p:Path):
 rel=p.relative_to(ROOT).as_posix()
 if rel in {'MANIFEST.json','SHA256SUMS.txt'}: return False
 if rel.startswith('results/') or rel.startswith('.cache/'): return False
 if '/__pycache__/' in '/'+rel or rel.endswith('.pyc'): return False
 return p.is_file()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
rows=[]
for p in sorted((x for x in ROOT.rglob('*') if tracked(x)), key=lambda x:x.relative_to(ROOT).as_posix()):
 rows.append({'bytes':p.stat().st_size,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
manifest={'file_count':len(rows),'files':rows,'repository_version':'1.0.0','schema_version':'1.0'}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+"\n",encoding='utf-8')
(ROOT/'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in rows),encoding='utf-8')
print(json.dumps({'manifest_records':len(rows),'status':'REGENERATED'},indent=2))
