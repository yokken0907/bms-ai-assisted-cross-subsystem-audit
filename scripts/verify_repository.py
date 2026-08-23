#!/usr/bin/env python3
from pathlib import Path
import csv, hashlib, json, py_compile, re, sys, zipfile
from urllib.parse import unquote
try:
 import yaml
except Exception as e:
 print({'pass':False,'errors':['PyYAML unavailable: '+str(e)]}); raise SystemExit(1)
ROOT=Path(__file__).resolve().parents[1]; errors=[]; details={}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def tracked_file(path):
 rel=path.relative_to(ROOT).as_posix()
 if rel in {'MANIFEST.json','SHA256SUMS.txt'}: return False
 if rel.startswith('results/') or rel.startswith('.cache/'): return False
 if '/__pycache__/' in '/'+rel or rel.endswith('.pyc'): return False
 return path.is_file()
# manifest and SHA inventory
manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8')); expected={r['path']:r for r in manifest['files']}
for rel,row in expected.items():
 p=ROOT/rel
 if not p.is_file(): errors.append('missing '+rel); continue
 if sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes']: errors.append('manifest mismatch '+rel)
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if tracked_file(p)}
for rel in sorted(actual-set(expected)): errors.append('unmanifested '+rel)
for rel in sorted(set(expected)-actual): errors.append('manifest-only '+rel)
sha_rows={}
for line in (ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
 if not line.strip(): continue
 try: h,n=line.split(None,1); n=n.strip().lstrip('*')
 except ValueError: errors.append('malformed SHA256SUMS line '+line); continue
 sha_rows[n]=h
if set(sha_rows)!=set(expected): errors.append('SHA256SUMS path set differs from MANIFEST')
for rel,h in sha_rows.items():
 if rel in expected and h!=expected[rel]['sha256']: errors.append('SHA256SUMS hash differs '+rel)
details['manifest_records']=len(expected)
# JSON parse
json_count=0
for p in ROOT.rglob('*.json'):
 if '/.cache/' in p.as_posix(): continue
 try: json.loads(p.read_text(encoding='utf-8')); json_count+=1
 except Exception as e: errors.append(f'JSON parse {p.relative_to(ROOT)}: {e}')
details['json_parsed']=json_count
# YAML/CFF parse
yaml_count=0
for p in list(ROOT.rglob('*.yml'))+list(ROOT.rglob('*.yaml'))+[ROOT/'CITATION.cff']:
 if not p.is_file(): continue
 try: yaml.safe_load(p.read_text(encoding='utf-8')); yaml_count+=1
 except Exception as e: errors.append(f'YAML parse {p.relative_to(ROOT)}: {e}')
details['yaml_parsed']=yaml_count
# CSV schema/count
expected_counts={'candidate_register_15.csv':15,'candidate_witnesses_15.csv':15,'canonical_branch_artifacts_14.csv':14,'case_register_17.csv':17,'controls_2.csv':2,'final_dispositions_15.csv':15,'mitigation_patterns_45.csv':45,'patent_document_technical_pattern_map_16.csv':16,'project_verification_gates_22.csv':22,'public_technical_sources_19.csv':19,'source_anchors_25.csv':25}
csv_report={}
for p in ROOT.rglob('*.csv'):
 try:
  with p.open(newline='',encoding='utf-8-sig') as f:
   r=csv.DictReader(f); rows=list(r); hdr=r.fieldnames
  if not hdr or any(h is None or h=='' for h in hdr): errors.append('CSV missing/invalid header '+p.relative_to(ROOT).as_posix())
  exp=expected_counts.get(p.name)
  if exp is not None and len(rows)!=exp: errors.append(f'CSV count {p.name}: {len(rows)} != {exp}')
  csv_report[p.name]=len(rows)
 except Exception as e: errors.append(f'CSV parse {p.relative_to(ROOT)}: {e}')
details['csv_rows']=csv_report
# Python syntax
py_count=0
for p in ROOT.rglob('*.py'):
 try: compile(p.read_text(encoding='utf-8'),str(p),'exec'); py_count+=1
 except Exception as e: errors.append(f'Python syntax {p.relative_to(ROOT)}: {e}')
details['python_syntax_checked']=py_count
# ZIP/DOCX path safety and collisions
archive_count=0
for p in list(ROOT.rglob('*.zip'))+list(ROOT.rglob('*.docx')):
 try:
  with zipfile.ZipFile(p) as z:
   names=z.namelist(); seen=set(); folded=set()
   for n in names:
    norm=n.replace('\\','/'); parts=[x for x in norm.split('/') if x not in ('','.')] 
    if norm.startswith('/') or re.match(r'^[A-Za-z]:',norm) or '..' in parts: errors.append('unsafe archive path '+p.relative_to(ROOT).as_posix()+': '+n)
    if norm in seen: errors.append('duplicate archive path '+p.relative_to(ROOT).as_posix()+': '+n)
    cf=norm.casefold()
    if cf in folded and norm not in seen: errors.append('case-collision archive path '+p.relative_to(ROOT).as_posix()+': '+n)
    seen.add(norm); folded.add(cf)
   archive_count+=1
 except zipfile.BadZipFile as e: errors.append('bad archive '+p.relative_to(ROOT).as_posix()+': '+str(e))
details['archives_path_safety_checked']=archive_count
# broken relative markdown links
link_re=re.compile(r'!?\[[^\]]*\]\(([^)]+)\)'); checked=0
for p in ROOT.rglob('*.md'):
 text=p.read_text(encoding='utf-8',errors='replace')
 for raw in link_re.findall(text):
  target=raw.strip().strip('<>')
  if not target or target.startswith(('#','http://','https://','mailto:','data:')): continue
  target=unquote(target.split('#',1)[0].split('?',1)[0])
  if not target: continue
  checked+=1
  q=(p.parent/target).resolve()
  try: q.relative_to(ROOT.resolve())
  except ValueError: errors.append('relative link escapes repository '+p.relative_to(ROOT).as_posix()+': '+raw); continue
  if not q.exists(): errors.append('broken relative link '+p.relative_to(ROOT).as_posix()+': '+raw)
details['relative_links_checked']=checked
print(json.dumps({'pass':not errors,'errors':errors,'details':details},indent=2)); raise SystemExit(0 if not errors else 1)
