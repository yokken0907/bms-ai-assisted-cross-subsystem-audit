#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES={r['case_id']:r for r in json.loads((ROOT/'data/case_register_17.json').read_text())}
PARSERS={
 'BMSA01-F01':'json','BMSA03-F01':'json','BMSA04-F01':'bmsa04','BMSA06-F01':'json','BMSA11-F01':'json',
 'BMSA02-C01':'json','BMSA06-C01':'bmsa06','BMSA05-F01':'json','BMSA07-F01':'bmsa07','BMSA08-F02':'bmsa08_f02',
 'BMSA09-F03':'json','BMSA10-F01':'json','BMSA08-F01':'bmsa08_f01','BMSA09-F01':'json','BMSA09-F02':'json',
 'BMSA10-F02':'json','BMSA10-F03':'json'}

def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True); return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def source_includes(src):
 first=src/'src/app/main/include'; dirs=[first] if first.is_dir() else []
 dirs.extend(sorted(x for x in (src/'src/app').rglob('*') if x.is_dir() and 'bootloader' not in x.parts and x!=first))
 fr=src/'src/os/freertos'
 if fr.is_dir(): dirs.extend(sorted(x for x in fr.rglob('*') if x.is_dir()))
 return [a for d in dirs for a in ('-I',str(d))]
def parse(kind,s):
 if kind=='json': return json.loads(s.strip())
 if kind=='bmsa04':
  rows=list(csv.reader(x for x in s.splitlines() if x.strip())); volts=[int(x[0]) for x in rows]; args=[int(x[1]) for x in rows]; soc=[float(x[2]) for x in rows]; dod=[int(x[3]) for x in rows]
  ok=len(rows)==100 and min(volts)==2716 and max(volts)==4123 and set(args)<={2,3,4} and all(abs(x)<1e-12 for x in soc) and set(dod)=={12600000}
  return {'pass':ok,'scenario_count':len(rows),'argument_min':min(args),'argument_max':max(args),'zero_soc_count':sum(abs(x)<1e-12 for x in soc),'constant_dod':len(set(dod))==1}
 if kind=='bmsa06':
  raw=re.search(r'RAW_ADC_MV=(\d+)',s); temp=re.search(r'CONVERTED_TEMPERATURE_DDEGC=(-?\d+)',s); ok=bool(raw and temp and int(raw.group(1))==0 and int(temp.group(1))==1664 and 'EXACT_ACQUISITION_BRIDGE_PASS' in s)
  return {'pass':ok,'raw_adc_mV':int(raw.group(1)) if raw else None,'converted_temperature_ddegC':int(temp.group(1)) if temp else None}
 if kind=='bmsa07':
  vals={k:int(v) for k,v in re.findall(r'(DIAG_DELAY_\d+ms)=(\d+)',s)}; return {'pass':vals=={'DIAG_DELAY_1000ms':1000,'DIAG_DELAY_2000ms':1000},'values_ms':vals}
 if kind=='bmsa08_f01':
  det=re.search(r'summary_detected_indices=(\d+)',s); miss=re.search(r'summary_missed_indices=(\d+)',s); carry='carryover_actual_string1=1 carryover_reference_string1=0' in s; ok=bool(det and miss and int(det.group(1))==2 and int(miss.group(1))==17 and carry)
  return {'pass':ok,'detected_indices':int(det.group(1)) if det else None,'missed_indices':int(miss.group(1)) if miss else None,'cross_string_carryover':carry}
 if kind=='bmsa08_f02':
  a=re.search(r'actual_substate=(\d+) actual_plus_requests=(\d+) actual_closed=(\d+) actual_count=(\d+) actual_fatal_checks=(\d+) actual_request_checks=(\d+)',s); b=re.search(r'reference_substate=(\d+) reference_plus_requests=(\d+) reference_closed=(\d+) reference_count=(\d+)',s); ok=bool(a and b and tuple(map(int,a.groups()))==(0,4,0,1,0,0) and tuple(map(int,b.groups()))==(2,1,1,2))
  return {'pass':ok,'actual':list(map(int,a.groups())) if a else None,'comparator':list(map(int,b.groups())) if b else None}
 raise ValueError(kind)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--output',type=Path,default=Path('results/witness_replay.json')); a=ap.parse_args(); src=a.source.resolve(); w=ROOT/'witnesses'; results=[]
 if not (src/'src').is_dir(): raise SystemExit('source directory does not look like foxBMS root')
 with tempfile.TemporaryDirectory(prefix='bms-witness-') as td:
  build=Path(td)
  for cid,row in CASES.items():
   f=w/row['witness_file']; kind='python' if f.suffix=='.py' else 'c'; variants=[]
   if kind=='python':
    for rep in (1,2):
     rr=run([sys.executable,str(f),'--source',str(src)]); parsed=parse(PARSERS[cid],rr['stdout']) if rr['returncode']==0 else {}; variants.append({'repeat':rep,'run':rr,'parsed':parsed,'pass':rr['returncode']==0 and parsed.get('pass') is True})
   else:
    for opt in ('-O0','-O2'):
     exe=build/(cid.lower().replace('-','_')+'_'+opt[1:].lower()); cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-Wno-cpp',opt,str(f)]
     if cid=='BMSA07-F01': cmd.extend(source_includes(src)); cmd.extend(['-I',str(w)])
     cmd.extend(['-lm','-o',str(exe)]); cc=run(cmd); rr=run([str(exe)]) if cc['returncode']==0 else {'command':[str(exe)],'returncode':None,'stdout':'','stderr':'not executed'}; parsed=parse(PARSERS[cid],rr['stdout']) if rr['returncode']==0 else {}; variants.append({'optimization':opt,'compile':cc,'run':rr,'parsed':parsed,'pass':cc['returncode']==0 and rr['returncode']==0 and parsed.get('pass') is True})
   equal=len(variants)==2 and variants[0]['parsed']==variants[1]['parsed']; passed=all(x['pass'] for x in variants) and equal
   results.append({'case_id':cid,'role':row['role'],'lane':row['lane'],'publication_facing_title':row['publication_facing_title'],'witness_file':row['witness_file'],'variants':variants,'optimization_or_repeat_consistent':equal,'pass':passed})
 payload={'case_count':len(results),'candidate_count':sum(x['role']=='UPSTREAM_CANDIDATE' for x in results),'control_count':sum(x['role']=='CONTROL' for x in results),'all_pass':all(x['pass'] for x in results),'results':results}
 out=(ROOT/a.output) if not a.output.is_absolute() else a.output; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps({'pass':payload['all_pass'],'case_count':17,'output':str(out)},indent=2)); raise SystemExit(0 if payload['all_pass'] else 1)
if __name__=='__main__': main()
