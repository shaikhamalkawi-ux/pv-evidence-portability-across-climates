#!/usr/bin/env python3
"""Project 66 Gate02: exact alpha-cut preference sensitivity (NOT PV measurement uncertainty).

Input 1 is the frozen, public R16 190-row derived ledger. Input 2 is the
11-row published annual-yield table transcribed exactly from R19 Supplement S2,
whose source is Marion et al. (2014), DOI 10.1016/j.solener.2014.10.017.

All fuzzy supports are expressly analyst-chosen preference stress scenarios, not
laboratory elicitation or an uncertainty distribution. No original PV raw data.
"""
import csv, json, hashlib
from pathlib import Path
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction
getcontext().prec=36
P=Path(__file__).resolve().parent
LEDGER='R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv'
YIELDS='R19_S2_COCOA_EUGENE_ANNUAL_FINAL_YIELDS.csv'
EXPECTED_LEDGER='45060d415faa8ed84f5b1212a36893e2401913616031deddf73e244d43bb3c9d'
EXPECTED_YIELDS='5ad0da15408d0953e9b92d98bf365c8e11082439303f2b9f5cc2f49d4ba9c129'
D=lambda x: Decimal(str(x))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(name):
 with (P/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write_csv(name,rows,cols=None):
 if cols is None:cols=list(rows[0])
 with (P/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
def sign(x):
 return 'worse' if x>0 else 'better' if x<0 else 'tie'
def mu(x,l,m,u):
 if x<l or x>u:return D(0)
 if x==m:return D(1)
 if x<m:return (x-l)/(m-l)
 return (u-x)/(u-m)
def alpha_cut(l,m,u,a):return l+a*(m-l),u-a*(u-m)
def alpha_cost_state(A,B,lo,hi):
 low=min(A+B*lo,A+B*hi);high=max(A+B*lo,A+B*hi)
 if low>0:return 'necessarily_worse'
 if high<0:return 'necessarily_better'
 if low==high==0:return 'exact_tie'
 if low==0 or high==0:return 'boundary_tie_possible'
 return 'both_signs_possible'
def max_mu_on_segment(start,stop,l,m,u):
 left=max(start,l);right=min(stop,u)
 if left>right:return D(0)
 if left<=m<=right:return D(1)
 return max(mu(left,l,m,u),mu(right,l,m,u))
def pi_and_n_interval(start,stop,l,m,u):
 """Possibility and necessity of preference q falling in [start,stop).

    Closed interval endpoints give same sup for continuous triangular membership.
 """
 if start>=stop:return D(0),D(0)
 pi=max_mu_on_segment(start,stop,l,m,u)
 pi_not=max(max_mu_on_segment(l,start,l,m,u),max_mu_on_segment(stop,u,l,m,u))
 n=D(1)-pi_not
 return max(D(0),min(D(1),pi)),max(D(0),min(D(1),n))
def strv(x):return format(x,'f') if isinstance(x,Decimal) else str(x)

assert sha(P/LEDGER)==EXPECTED_LEDGER,'Frozen R16 ledger SHA mismatch'
assert sha(P/YIELDS)==EXPECTED_YIELDS,'R19 Table S2 transcription SHA mismatch'
ledger=read_csv(LEDGER)
assert len(ledger)==190 and len({(r['target_id'],r['source_order']) for r in ledger})==190
complete=[r for r in ledger if r['delta_mean_pair_cells'] and int(r['n_unresolved'])==0]
assert len(complete)==188
correct_complete=[r for r in complete if r['source_winner_correct']=='True']
assert len(correct_complete)==184
mean_better=[r for r in correct_complete if D(r['delta_mean_pair_cells'])<0]
assert len(mean_better)==79
assert sum(r['n_wrong']!='0' for r in mean_better)==0

# Core analytical classification for ALL lambda > 0: no fuzzy weight elicitation needed.
exact_rows=[]; class_counts=Counter(); mixed=[]
for r in mean_better:
 A,B=D(r['delta_K_all']),D(r['delta_N_mod_cell'])
 assert A==A.to_integral_value() and B==B.to_integral_value()
 if A<=0 and B<=0 and (A<0 or B<0): category='always_better'
 elif A>=0 and B>=0 and (A>0 or B>0):category='always_worse'
 elif A*B<0:category='weight_sensitive'
 else:raise AssertionError((r['target_id'],A,B))
 class_counts[category]+=1
 rr={'target_id':r['target_id'],'source_order':r['source_order'],
     'delta_mean_pair_cells':r['delta_mean_pair_cells'],'delta_K_all':strv(A),'delta_N_mod_cell':strv(B),
     'all_positive_weights_category':category,'exact_lambda_switch':''}
 if category=='weight_sensitive':
  critical=Fraction(-int(A),int(B));rr['exact_lambda_switch']=str(critical)
  mixed.append((r,A,B,critical))
 exact_rows.append(rr)
assert class_counts=={'always_better':34,'always_worse':30,'weight_sensitive':15},class_counts
assert sum(int(D(r['delta_K_all'])>0 and D(r['delta_N_mod_cell'])>0) for r in mean_better)==21
assert len({r['target_id'] for r in mean_better})==25
write_csv('StageA_Exact_Dominance_79.csv',exact_rows)

# Three triangular fuzzy memberships share the same deliberately broad support.
# L=.05<smallest switch; U=10>largest. Mode is stress-tested rather than elicited.
L,M,U=D('.05'),D('1'),D('10')
shape_modes=[D('.25'),D('1'),D('4')]
alphas=[D('0'),D('.25'),D('.5'),D('.75'),D('.9'),D('1')]
alpha_rows=[];shape_summary=[];scenario_case_rows=[]
for m in shape_modes:
 for alpha in alphas:
  lo,hi=alpha_cut(L,m,U,alpha)
  count=Counter(alpha_cost_state(D(r['delta_K_all']),D(r['delta_N_mod_cell']),lo,hi) for r in mean_better)
  assert sum(count.values())==79
  shape_summary.append(dict(mode=strv(m),alpha=strv(alpha),lambda_low=strv(lo),lambda_high=strv(hi),
    necessarily_better=count['necessarily_better'],necessarily_worse=count['necessarily_worse'],
    both_signs_possible=count['both_signs_possible'],boundary_tie_possible=count['boundary_tie_possible'],
    exact_tie=count['exact_tie']))
  for r in mean_better:
   A,B=D(r['delta_K_all']),D(r['delta_N_mod_cell'])
   alpha_rows.append(dict(target_id=r['target_id'],source_order=r['source_order'],mode=strv(m),alpha=strv(alpha),
    lambda_low=strv(lo),lambda_high=strv(hi),delta_cost_low=strv(min(A+B*lo,A+B*hi)),
    delta_cost_high=strv(max(A+B*lo,A+B*hi)),
    classification=alpha_cost_state(A,B,lo,hi)))
 for r,A,B,critical in mixed:
  t=D(critical.numerator)/D(critical.denominator)
  center=A+B*m
  if center==0:
   poss_better=poss_worse=D(1);necess_better=necess_worse=D(0)
  else:
   cross=mu(t,L,m,U)
   if center>0:
    poss_worse=D(1);necess_worse=D(1)-cross;poss_better=cross;necess_better=D(0)
   else:
    poss_better=D(1);necess_better=D(1)-cross;poss_worse=cross;necess_worse=D(0)
  scenario_case_rows.append(dict(target_id=r['target_id'],source_order=r['source_order'],
     delta_K_all=strv(A),delta_N_mod_cell=strv(B),lambda_critical_exact=str(critical),mode=strv(m),
     modal_outcome=sign(center),critical_alpha=strv(mu(t,L,m,U)),
     possibility_better=strv(poss_better),necessity_better=strv(necess_better),
     possibility_worse=strv(poss_worse),necessity_worse=strv(necess_worse)))
write_csv('StageA_Fuzzy_AlphaCut_Summary.csv',shape_summary)
write_csv('StageA_Fuzzy_AlphaCut_Cases.csv',alpha_rows)
write_csv('StageA_Possibility_Necessity_15.csv',scenario_case_rows)

# Check representative alpha cuts, exact endpoints (no Monte Carlo).
def row_count(m,alpha):
 return next(x for x in shape_summary if D(x['mode'])==D(m) and D(x['alpha'])==D(alpha))
assert {k:int(row_count(1,0)[k]) for k in ['necessarily_better','necessarily_worse','both_signs_possible']}=={
 'necessarily_better':34,'necessarily_worse':30,'both_signs_possible':15}
assert {k:int(row_count(1,D('.5'))[k]) for k in ['necessarily_better','necessarily_worse','both_signs_possible']}=={
 'necessarily_better':41,'necessarily_worse':32,'both_signs_possible':6}
assert {k:int(row_count(1,D('.75'))[k]) for k in ['necessarily_better','necessarily_worse','both_signs_possible']}=={
 'necessarily_better':42,'necessarily_worse':34,'both_signs_possible':3}
assert {k:int(row_count(D('.25'),D('.5'))[k]) for k in ['necessarily_better','necessarily_worse','both_signs_possible']}=={
 'necessarily_better':35,'necessarily_worse':30,'both_signs_possible':14}
assert {k:int(row_count(D('4'),D('.5'))[k]) for k in ['necessarily_better','necessarily_worse','both_signs_possible']}=={
 'necessarily_better':43,'necessarily_worse':33,'both_signs_possible':3}
critical=Counter(str(k) for _,_,_,k in mixed)
assert critical=={'1/14':1,'1/4':1,'2/5':6,'1/2':1,'2/3':1,'1':2,'3':1,'4':2},critical

# Separate stage B fuzzy q: derive all 11 deficits from the SOURCE-TABULATED
# integer annual final yields in R19 Supplement Table S2 (p. 3).
yields=read_csv(YIELDS)
assert len(yields)==11 and len({y['module_id'] for y in yields})==11
Yc=max(D(y['cocoa_annual_final_yield_hours']) for y in yields)
Ye=max(D(y['eugene_annual_final_yield_hours']) for y in yields)
assert Yc==2019 and Ye==1482
Lq,Mq,Uq=D('4.5'),D('5'),D('5.5')
qs=[];qtables=[]
for y in yields:
 sc=D('100')*(Yc-D(y['cocoa_annual_final_yield_hours']))/Yc
 tg=D('100')*(Ye-D(y['eugene_annual_final_yield_hours']))/Ye
 pi,ne=pi_and_n_interval(tg,sc,Lq,Mq,Uq)
 qtables.append(dict(module_id=y['module_id'],cocoa_yield_h=y['cocoa_annual_final_yield_hours'],
     eugene_yield_h=y['eugene_annual_final_yield_hours'],cocoa_deficit_pct=strv(sc),
     eugene_deficit_pct=strv(tg),is_nominal_false_exclusion_at_q5=str(tg<=Mq<sc),
     possibility_of_false_exclusion=strv(pi),necessity_of_false_exclusion=strv(ne)))
 qs.append((y['module_id'],tg,sc))
write_csv('StageB_Fuzzy_q_Module_Possibility.csv',qtables)
assert {y['module_id'] for y in qtables if y['is_nominal_false_exclusion_at_q5']=='True'}=={
 'HIT05667','aSiTandem72-46','aSiTriple28324'}
assert [q for q in qtables if q['module_id']=='aSiTandem72-46'][0]['necessity_of_false_exclusion'].startswith('0.104011887')

def false_count(q):return sum(t<=q<s for _,t,s in qs)
breaks=sorted(set([Lq,Uq]+[v for _,t,s in qs for v in [t,s] if Lq<v<Uq]))
step=[]
for a,b in zip(breaks[:-1],breaks[1:]):
 mid=(a+b)/2
 if a==b:continue
 step.append(dict(q_from_pct=strv(a),q_to_pct=strv(b),false_exclusion_count=false_count(mid),
   possibility_of_interval=strv(max_mu_on_segment(a,b,Lq,Mq,Uq))))
assert [t['false_exclusion_count'] for t in step]==[3,2,3,4],step
write_csv('StageB_q_Exact_Count_Segments.csv',step)
q_alpha=[]
for alpha in [D(0),D('.25'),D('.5'),D('.75'),D('.9'),D(1)]:
 lo,hi=alpha_cut(Lq,Mq,Uq,alpha)
 relevant=[false_count(lo),false_count(hi)]
 for _,t,s in qs:
  if lo<t<hi:relevant.append(false_count(t))
  if lo<s<hi:relevant.append(false_count(s))
 # step values on interior gaps are needed because same breakpoint yields different side limits
 bnds=sorted(set([lo,hi]+[v for _,t,s in qs for v in [t,s] if lo<v<hi]))
 for a,b in zip(bnds[:-1],bnds[1:]):relevant.append(false_count((a+b)/2))
 q_alpha.append(dict(alpha=strv(alpha),q_low=strv(lo),q_high=strv(hi),
  minimum_nominal_false_exclusions=min(relevant),maximum_nominal_false_exclusions=max(relevant)))
assert [(int(r['minimum_nominal_false_exclusions']),int(r['maximum_nominal_false_exclusions'])) for r in q_alpha]==[
 (2,4),(2,4),(2,3),(2,3),(3,3),(3,3)],q_alpha
write_csv('StageB_Fuzzy_q_AlphaCut_Range.csv',q_alpha)

# Low-level invariants for possibility grades: these are not probabilities.
for r in scenario_case_rows:
 for a,b in [('possibility_better','necessity_better'),('possibility_worse','necessity_worse')]:
  assert D(0)<=D(r[b])<=D(r[a])<=D(1)
for r in qtables:
 assert D(0)<=D(r['necessity_of_false_exclusion'])<=D(r['possibility_of_false_exclusion'])<=D(1)

summary={
 'status':'PASS','type':'conditional_fuzzy_preference_interpretation_not_measurement_uncertainty',
 'source_ledger_sha256':EXPECTED_LEDGER,'source_supplement_table_s2_transcription_sha256':EXPECTED_YIELDS,
 'source_supplement_pdf_sha256':'ec5f8c1003c8444d927f5c90819e0efc33eb5169321e9255d4a875b3048275f3',
 'stageA':{'historical_replays':190,'complete_correct_winner':184,'mean_improving_correct_replays':79,
   'unique_mean_improving_targets':25,'always_better':34,'always_worse':30,'switching':15,'strict_both_worse':21,
   'different_exact_switches':8,'scenarios':shape_summary},
 'stageB':{'modules':len(yields),'q_mode_pct':'5','q_triangle_pct':['4.5','5','5.5'],
   'nominal_false_exclusions_at_q5':false_count(Mq),'exact_segments':step,'alpha_summary':q_alpha},
 'claim_boundary':'No elicited stakeholder weights, no calibrated I-V uncertainty, no new independent PV experiments, no frequency/probability interpretation.'
}
(P/'Gate02_Results_and_QA.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({
 'status':'PASS','stageA_exact':dict(class_counts),
 'stageA_broad_alpha_0':row_count(1,0),
 'stageA_broad_alpha_half':row_count(1,D('.5')),
 'stageA_broad_alpha_threequarters':row_count(1,D('.75')),
 'stageB_3_nominal':false_count(Mq),'stageB_segments':step,
 'stageB_alpha':q_alpha},indent=2))
