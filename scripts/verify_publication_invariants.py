#!/usr/bin/env python3
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[1]
exp=json.loads((ROOT/'data/publication_invariants.json').read_text())
cands=json.loads((ROOT/'data/candidate_register_15.json').read_text())
ctrl=json.loads((ROOT/'data/controls_2.json').read_text())
case17=json.loads((ROOT/'data/case_register_17.json').read_text())
anchors=json.loads((ROOT/'data/source_anchors_25.json').read_text())
mit=json.loads((ROOT/'data/mitigation_patterns_45.json').read_text())
sources=json.loads((ROOT/'data/public_technical_sources_19.json').read_text())
pat=json.loads((ROOT/'data/patent_document_technical_pattern_map_16.json').read_text())
gates=json.loads((ROOT/'data/project_verification_gates_22.json').read_text())
errs=[]
def ck(ok,msg):
 if not ok: errs.append(msg)
ck(len(cands)==15,'candidate count'); ck(len(ctrl)==2,'control count'); ck(len(case17)==17,'register count')
ck(collections.Counter(x['lane'] for x in cands)==collections.Counter({'VALUE_DATA_FLOW':5,'STATE_TIME':5,'COMMUNICATION_CONFIGURATION':5}),'candidate lane 5/5/5')
ck(sum(x['witness_file'].endswith('.c') for x in cands)==13,'13 candidate C witnesses'); ck(sum(x['witness_file'].endswith('.py') for x in cands)==2,'2 candidate Python witnesses')
ck(len(anchors)==25 and len({x['case_id'] for x in anchors})==15,'25 anchors / 15 cases'); ck(len(mit)==45,'45 mitigation mappings'); ck(len(sources)==19,'19 unique public sources')
# Source uses are preserved in frozen raw mitigation map
raw=json.loads((ROOT/'evidence/frozen/CROSS_BRANCH__BMSA13_MITIGATION_MAP_FROZEN.json').read_text()); ck(sum(len(x['public_sources']) for x in raw)==46,'46 public-source uses')
ck(len(pat)==16,'16 patent mappings'); ck(len({x['publication'] for x in pat})==13,'13 unique patent publications'); ck(sum(x['directness']=='TECHNICALLY_DIRECT_PATTERN' for x in pat)==11,'11 direct mappings'); ck(sum(x['directness']=='DOMAIN_ADJACENT_PATTERN' for x in pat)==5,'5 adjacent mappings')
ck(len(gates)==22 and all(x['pass'] for x in gates),'22 verification gates')
ck(sum(x['candidate_specific_effective_mitigation_status']=='ESTABLISHED' for x in cands)==0,'0/15 effective mitigation established'); ck(sum(bool(x['residual_risk_declared']) for x in cands)==0,'0 residual risk'); ck(sum(bool(x['product_or_safety_conclusion']) for x in cands)==0,'0 product/safety conclusions')
ck(next(x for x in cands if x['case_id']=='BMSA10-F02')['publication_facing_title']=='Public BMS state-machine test-surface traceability candidate','BMSA10-F02 publication title')
print(json.dumps({'pass':not errs,'errors':errs},indent=2)); raise SystemExit(0 if not errs else 1)
