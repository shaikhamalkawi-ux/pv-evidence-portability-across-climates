#!/usr/bin/env python3
"""Independent simple-precision/output-path QA of the fuzzy preference stress experiment.
This DOES NOT independently validate source physical measurements or elicitation.
"""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
from decimal import Decimal
P=Path(__file__).resolve().parent
read=lambda name:list(csv.DictReader((P/name).open(newline='',encoding='utf-8')))
ledger=read('R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv')
assert len(ledger)==190
filtered=[r for r in ledger if r['delta_mean_pair_cells'] and int(r['n_unresolved'])==0 and r['source_winner_correct']=='True' and float(r['delta_mean_pair_cells'])<0]
assert len(filtered)==79
exp=[]
for r in filtered:
 a=int(float(r['delta_K_all']));b=int(float(r['delta_N_mod_cell']))
 t='always_better' if a<=0 and b<=0 and min(a,b)<0 else 'always_worse' if a>=0 and b>=0 and max(a,b)>0 else 'weight_sensitive'
 exp.append((r['target_id'],r['source_order'],t))
orig=read('StageA_Exact_Dominance_79.csv')
assert set((r['target_id'],r['source_order'],r['all_positive_weights_category']) for r in orig)==set(exp)
assert Counter(r['all_positive_weights_category'] for r in orig)=={'always_better':34,'always_worse':30,'weight_sensitive':15}
assert len(read('StageA_Fuzzy_AlphaCut_Cases.csv'))==79*3*6
all_cases=read('StageA_Fuzzy_AlphaCut_Cases.csv')
for r in all_cases:
 lo=float(r['lambda_low']);hi=float(r['lambda_high']);a=float(r['delta_cost_low']);b=float(r['delta_cost_high']);assert a<=b+1e-10
 if r['classification']=='necessarily_better':assert b<-1e-10
 if r['classification']=='necessarily_worse':assert a>1e-10
 if r['classification']=='both_signs_possible':assert a<-1e-10 and b>1e-10
 if r['classification']=='exact_tie':assert abs(a)<1e-10 and abs(b)<1e-10
 assert lo<=hi
modes=read('StageA_Fuzzy_AlphaCut_Summary.csv')
assert len(modes)==18
for mode in ('0.25','1','4'):
 ss=sorted([r for r in modes if r['mode']==mode],key=lambda r:float(r['alpha']))
 assert len(ss)==6
 assert all(float(ss[i]['lambda_low'])<=float(ss[i+1]['lambda_low']) for i in range(5))
 assert all(float(ss[i]['lambda_high'])>=float(ss[i+1]['lambda_high']) for i in range(5))
 assert all(int(x['necessarily_better'])+int(x['necessarily_worse'])+int(x['both_signs_possible'])+int(x['boundary_tie_possible'])+int(x['exact_tie'])==79 for x in ss)
assert len(read('StageA_Possibility_Necessity_15.csv'))==45
# Independent source-yield reconstruction: the published 11-module table uses
# Cocoa max=2019h and Eugene max=1482h.
y=read('R19_S2_COCOA_EUGENE_ANNUAL_FINAL_YIELDS.csv')
assert len(y)==11
src={r['module_id']:(float(r['cocoa_annual_final_yield_hours']),float(r['eugene_annual_final_yield_hours'])) for r in y}
assert len(src)==11
cs=max(c for c,e in src.values());es=max(e for c,e in src.values());assert (cs,es)==(2019,1482)
def n_exclusions(q):
 return sum(100*(1-e/es)<=q<100*(1-c/cs) for c,e in src.values())
assert n_exclusions(5.)==3
for q,n in [(4.5,3),(5.0519,3),(5.0521,2),(5.1281,2),(5.1283,3),(5.3307,4),(5.5,4)]:
 assert n_exclusions(q)==n,(q,n_exclusions(q),n)
Q=read('StageB_Fuzzy_q_AlphaCut_Range.csv')
for r in Q:
 lo=float(r['q_low']);hi=float(r['q_high']);v=[n_exclusions(lo+i*(hi-lo)/1000) for i in range(1001)]
 assert min(v)==int(r['minimum_nominal_false_exclusions']),(r,min(v))
 assert max(v)==int(r['maximum_nominal_false_exclusions']),(r,max(v))
Qt=read('StageB_Fuzzy_q_Module_Possibility.csv')
assert len(Qt)==11
nom={r['module_id'] for r in Qt if r['is_nominal_false_exclusion_at_q5']=='True'}
assert nom=={'aSiTandem72-46','aSiTriple28324','HIT05667'}
assert len([x for x in Qt if float(x['possibility_of_false_exclusion'])>0])==5
assert len([x for x in Qt if float(x['necessity_of_false_exclusion'])==1])==2
assert all(0<=float(r['necessity_of_false_exclusion'])<=float(r['possibility_of_false_exclusion'])<=1 for r in Qt)
result={'status':'PASS','scope':'derived-only computational independence, not field-data verification',
 'stageA_rows':len(orig),'stageA_alpha_cases':len(all_cases),'stageA_fuzzy_modal_scenarios':3,
 'stageB_physical_units':len(Qt),'stageB_q5_count':3,'stageB_qsupport_min_max':[2,4],
 'third_party_raw_redistributed':False}
(P/'Independent_QA.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
