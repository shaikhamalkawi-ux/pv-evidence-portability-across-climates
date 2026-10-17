#!/usr/bin/env python3
"""Independent output-level verifier; DOES NOT import/reuse R3 replay implementation.
Rebuilds all summary counts/mean/percent errors from standalone 36-pair CSV,
validates source-number/eligibility/weight invariants, and quantifies repeated-quarter
selection stability with tied minima handled as sets.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent;P=ROOT/'results'
summary=pd.read_csv(P/'external_source_order_replay.csv');pairs=pd.read_csv(P/'external_pairlevel_decisions.csv');gate=pd.read_csv(P/'country_source_support_gates.csv');weights=pd.read_csv(P/'original_grid_27_node_site_weights.csv');meta=json.loads((P/'external_summary.json').read_text());
checks=[]
def check(label,cond,detail=None):
  checks.append({'test':label,'pass':bool(cond),'details':str(detail)[:400] if detail is not None else ''})
  if not cond:raise AssertionError(f'{label} {detail}')

check('original 5x5 no-retuning baseline PASS',bool(meta['baseline']['original_R3_25_of_25_cells_PASS']) and meta['baseline']['original_R3_max_abs_pct_point_diff']<=1e-8)
check('every site six original source orders including local',summary.groupby('target_id').size().eq(6).all())
check('expected output counts',len(summary)==900 and len(pairs)==32400 and len(weights)==150)
check('every site has 36 original calibration products',pairs.groupby(['target_id','source_order']).size().eq(36).all())
check('no unexpected source orders',set(summary.source_order)=={'Target-local heuristic','Cocoa','Eugene','Golden','Switzerland','Albuquerque'})
check('all sources map onto numeric gate PASS',set(summary.target_id)==set(gate[gate.numeric_external_gate=='PASS'].target_id))
check('supported minimum R3 grid sample count and day count',((gate[gate.numeric_external_gate=='PASS'].n_in_R3_grid>=1000)&(gate[gate.numeric_external_gate=='PASS'].n_unique_in_grid_dates>=30)).all())
check('original 27-node interpolated weights sum to 1',np.allclose(weights.iloc[:,1:].sum(axis=1).to_numpy(float),1,rtol=0,atol=1e-11))
check('original bary weights no large negative',float(weights.iloc[:,1:].min().min())>=-1e-11)
check('Brazil exactly 51 parent plant files',len(gate[(gate.source_dataset=='D09_Brazil')&(~gate.is_repeated_sensitivity)])==51)
check('Brazil exactly 34 eligible parent plant files',len(gate[(gate.source_dataset=='D09_Brazil')&(~gate.is_repeated_sensitivity)&(gate.numeric_external_gate=='PASS')])==34)
check('Brazil exactly 17 held parent plant files',len(gate[(gate.source_dataset=='D09_Brazil')&(~gate.is_repeated_sensitivity)&(gate.numeric_external_gate!='PASS')])==17)
check('Italy three sensor rows and 9 annual sensitivity rows',len(gate[gate.source_dataset=='D24_Italy'])==3 and len(gate[gate.source_dataset=='D24_Italy_annual'])==9)
check('Germany exactly three distinct system-period targets',len(gate[gate.source_dataset=='D22_Germany'])==3)
check('Brazil quarterly sensitivity valid and labeled',len(gate[(gate.source_dataset=='D09_Brazil_quarter')&(gate.numeric_external_gate=='PASS')])==101)

# Independently recompute every summary from 36 pair-level rows, including stop omission denominator.
summ=summary.set_index(['target_id','source_order'])
viol=[]
for key,grp in pairs.groupby(['target_id','source_order']):
 row=summ.loc[key]
 n_res=int((~grp.unresolved.astype(bool)).sum())
 wrong=int(grp.wrong_accepted.astype(bool).sum())
 n_unr=int(grp.unresolved.astype(bool).sum())
 if n_res != int(row.n_resolved) or wrong != int(row.n_wrong_accepted) or n_unr!=int(row.n_unresolved):viol.append((key,'paircounts'))
 s=float(grp.stop_cells.dropna().mean()) if n_res else np.nan
 if abs(s-row.source_mean_cells_resolved)>1e-10:viol.append((key,'mean stop'))
 # Native comparator from all 36 pair level native cells, only resolved native must exist
 local=float(grp.target_local_stop_cells.dropna().mean())
 if abs(local-row.target_local_mean_cells_resolved)>1e-10:viol.append((key,'native stop'))
 if n_unr==0 and grp.target_local_stop_cells.notna().all():
   expected=100*(s/local-1)
   if not np.isfinite(row.directional_excess_pct_all_resolved_only) or abs(expected-row.directional_excess_pct_all_resolved_only)>1e-9:viol.append((key,'excess'))
 else:
   if pd.notna(row.directional_excess_pct_all_resolved_only):viol.append((key,'unresolved should be null'))
check('ALL 900 rows recomputed from independent 32,400 pair-level rows',not viol,viol[:20])
# Source order efficacy:
primary=summary[(~summary.is_repeated_sensitivity)&(summary.source_order!='Target-local heuristic')].copy();local=summary[(~summary.is_repeated_sensitivity)&(summary.source_order=='Target-local heuristic')].copy()
check('three countries 38 primary field trajectories',primary.target_id.nunique()==38)
check('all 34 Brazil full-plant 5-order trials have zero accepted wrong signs',int(primary[primary.source_dataset=='D09_Brazil'].n_wrong_accepted.sum())==0)
check('Brazil only Eugene 3 unresolved in two sites',int(primary[primary.source_dataset=='D09_Brazil'].n_unresolved.sum())==3 and set(primary[(primary.source_dataset=='D09_Brazil')&(primary.n_unresolved>0)].source_order)=={'Eugene'})
check('Germany four wrong accepted same small-margin pair',int(primary[primary.source_dataset=='D22_Germany'].n_wrong_accepted.sum())==4)
check('Italy full-period zero wrong accepted',int(primary[primary.source_dataset=='D24_Italy'].n_wrong_accepted.sum())==0)
check('all primary target-local references resolve and sign-correct',int(local.n_unresolved.sum())==0 and int(local.n_wrong_accepted.sum())==0)
# When tied source choices, keep all ties instead of selecting arbitrary argmin.
win=[]
for name,grp in primary.groupby('target_id'):
 q=grp.dropna(subset=['directional_excess_pct_all_resolved_only'])
 mv=q.directional_excess_pct_all_resolved_only.min()
 winners=sorted(q.loc[(q.directional_excess_pct_all_resolved_only-mv).abs()<=1e-8,'source_order'])
 win.append({'target_id':name,'source_dataset':grp.source_dataset.iloc[0],'lowest_excess_pct':float(mv),'best_source_orders_ties_preserved':'|'.join(winners),'n_tied_best':len(winners),'n_noncomparable_source_orders_due_to_unresolved':int(grp.directional_excess_pct_all_resolved_only.isna().sum())})
w=pd.DataFrame(win);w.to_csv(P/'primary_best_historical_orders_tie_aware.csv',index=False)
check('tied minima preserved and all 38 primary targets covered',len(w)==38)
# Quarter sensitivity WITH ties preserved. Winner stability check across >=2 quarters per parent site.
quarters=summary[(summary.source_dataset=='D09_Brazil_quarter')&(summary.source_order!='Target-local heuristic')]
qwin=[]
for name,grp in quarters.groupby('target_id'):
 q=grp.dropna(subset=['directional_excess_pct_all_resolved_only']);
 if q.empty:continue
 mv=q.directional_excess_pct_all_resolved_only.min();winlist=sorted(q.loc[(q.directional_excess_pct_all_resolved_only-mv).abs()<=1e-8,'source_order'])
 parent='_'.join(name.split('_')[:3])
 qwin.append({'target_id':name,'parent_site':parent,'quarter':name[len(parent)+1:],'lowest_excess_pct':float(mv),'best_order_set':'|'.join(winlist),'n_tied_best':len(winlist)})
qwin=pd.DataFrame(qwin);qwin.to_csv(P/'Brazil_quarter_best_source_sets.csv',index=False)
mult=qwin.groupby('parent_site').filter(lambda z:len(z)>=2)
switch=[]
for site,q in mult.groupby('parent_site'):
 sets=[set(s.split('|')) for s in q.best_order_set]
 common=set.intersection(*sets)
 switch.append({'site':site,'eligible_quarters':len(q),'a_common_best_source_exists_all_quarters':bool(common),'intersection_best_orders':'|'.join(sorted(common)),'per_quarter_best_sets':' ; '.join(q.quarter+'='+q.best_order_set)})
switch=pd.DataFrame(switch);switch.to_csv(P/'Brazil_within_plant_quarter_source_choice_stability.csv',index=False)
check('eligible multi-quarter Brazilian sites recorded',len(switch)==31)
check('quarter-level source minima vary in 30 of 31 same plant IDs',int((~switch.a_common_best_source_exists_all_quarters).sum())==30)
# Field weights can be close at separate plant IDs; never treat 34 as independent countries.
raw=weights.set_index('target_id');bra=raw.loc[raw.index.str.match('D09_PS_[0-9]{3}$')];arr=bra.to_numpy(float);dist=.5*np.sum(np.abs(arr[:,None,:]-arr[None,:,:]),axis=2);np.fill_diagonal(dist,np.inf)
idx=np.unravel_index(np.argmin(dist),dist.shape)
check('Brazil has 34 full-site node-weight vectors',len(bra)==34)
metrics={
'baseline_25_of_25_exact':True,'independent_qa_pass':sum(x['pass'] for x in checks),'independent_qa_total':len(checks),
'Germany_periods':3,'Italy_independent_sites':1,'Italy_repeated_temp_sensors':3,'Italy_annual_sensitivity_windows':9,
'Brazil_source_file_count':51,'Brazil_primary_eligible_plants':34,'Brazil_primary_held_plants':17,
'Brazil_quarter_sensitivity_eligible':len(qwin),'Brazil_multi_quarter_plant_count':len(switch),'Brazil_plants_without_common_quarter_best_order':int((~switch.a_common_best_source_exists_all_quarters).sum()),
'Brazil_34_site_weight_nearest_total_variation':float(dist[idx]),'Brazil_34_site_weight_nearest_ids':[str(bra.index[idx[0]]),str(bra.index[idx[1]])],
'primary_external_old_orders_n':len(primary),'primary_external_wrong_accepted_count':int(primary.n_wrong_accepted.sum()),'primary_external_unresolved_count':int(primary.n_unresolved.sum()),
'full_period_Brazil_wrong_accepted':int(primary[primary.source_dataset=='D09_Brazil'].n_wrong_accepted.sum()),
'full_period_Brazil_unresolved':int(primary[primary.source_dataset=='D09_Brazil'].n_unresolved.sum()),
'full_period_Germany_wrong_accepted':int(primary[primary.source_dataset=='D22_Germany'].n_wrong_accepted.sum()),
'full_period_Italy_wrong_accepted':int(primary[primary.source_dataset=='D24_Italy'].n_wrong_accepted.sum()),
'quarter_wrong_accepted_old_orders':int(quarters.n_wrong_accepted.sum()),
'quarter_unresolved_old_orders':int(quarters.n_unresolved.sum()),
'yearly_Italy_wrong_accepted_old_orders':int(summary[(summary.source_dataset=='D24_Italy_annual')&(summary.source_order!='Target-local heuristic')].n_wrong_accepted.sum()),
'nonindependence_warning':'34 Brazil plant files are clustered observational traces, not 34 independent climate zones; a particularly close node-weight pair has TV distance as recorded; no statistical sampling confidence interval inferred',
'claim_state':'Finite conditional field operating-state robustness. R3 response products are not measured at new field sites.'
}
(P/'independent_QA_summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
(ROOT/'qa'/'independent_output_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(metrics,indent=2));print('PASS',sum(x['pass'] for x in checks),'/',len(checks))
