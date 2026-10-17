#!/usr/bin/env python3
"""Independent vectorized work-proxy test against original 32,400-row R4 CSV.
No physical time/savings inference. Reads original source ZIP as immutable input.
"""
from pathlib import Path
import io,zipfile,json,sys
import pandas as pd

def verify(archive,out):
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  p=pd.read_csv(io.BytesIO(z.read('results/external_pairlevel_decisions.csv')))
  runs=pd.read_csv(io.BytesIO(z.read('results/external_source_order_replay.csv')))
 assert len(p)==32400 and len(runs)==900
 primary=runs[~runs.is_repeated_sensitivity][['target_id','source_order']]
 x=p.merge(primary,on=['target_id','source_order'],how='inner',validate='many_to_one')
 assert len(x)==38*6*36
 # Deliberately independent formulation: each pair contributes its cell-count to
 # each endpoint module, and module maxima are summed once per order/target.
 v=x[x.stop_cells.notna()].copy()
 a=v[['target_id','source_order','module_a','stop_cells']].rename(columns={'module_a':'module'})
 b=v[['target_id','source_order','module_b','stop_cells']].rename(columns={'module_b':'module'})
 module_long=pd.concat([a,b],ignore_index=True)
 module_max=module_long.groupby(['target_id','source_order','module'],as_index=False).stop_cells.max()
 sums=module_max.groupby(['target_id','source_order']).stop_cells.sum().rename('N').reset_index()
 agg=x.groupby(['target_id','source_order']).agg(mean=('stop_cells','mean'),K=('stop_cells','max'),missing=('unresolved','sum'),wrong=('wrong_accepted','sum'),pairs=('stop_cells','size')).reset_index()
 agg=agg.merge(sums,on=['target_id','source_order'],validate='one_to_one')
 assert set(agg.pairs)=={36}
 agg.loc[agg.missing>0,['mean','K','N']]=float('nan')
 local=agg[agg.source_order=='Target-local heuristic'].set_index('target_id')
 hist=agg[agg.source_order!='Target-local heuristic'].copy()
 for key in ('mean','K','N'):
  hist['ref_'+key]=hist.target_id.map(local[key])
 completed=hist[hist.missing==0].copy()
 improved=completed[completed['mean']<completed['ref_mean']-1e-10]
 dual=improved[(improved.K>improved.ref_K)&(improved.N>improved.ref_N)]
 assert len(hist)==190 and len(completed)==188
 # Relative-weight sweep is a sensitivity ANALOGUE, not instrument timing.
 expected={0:40,0.01:42,0.1:41,1:35,10:33}
 for lam, count in expected.items():
  cost=improved.K+lam*improved.N
  refcost=improved.ref_K+lam*improved.ref_N
  assert int((cost>refcost+1e-9).sum())==count, (lam,count)
 assert len(improved)==79 and len(dual)==21
 assert improved.loc[improved.N>improved.ref_N].shape[0]==26
 assert improved.loc[improved.K>improved.ref_K].shape[0]==40
 assert dual.wrong.sum()==0
 assert dual.target_id.nunique()==10 and dual.target_id.str.startswith('D09_').all()
 example=completed[(completed.target_id=='D09_PS_001')&(completed.source_order=='Albuquerque')].iloc[0]
 assert (example.K,example.ref_K,example.N,example.ref_N)==(15,14,102,100)
 assert abs(example['mean']-258/36)<1e-12 and abs(example.ref_mean-285/36)<1e-12
 # Double-check every complete cost estimate against the independently previously
 # constructed per-run table (which used explicit graph-node incident pair loops).
 old=pd.read_csv(Path(out).parent/'primary_source_workload.csv')
 check=completed.merge(old,left_on=['target_id','source_order'],right_on=['target','source'],validate='one_to_one')
 assert len(check)==188
 assert (abs(check.N-check.modcells)<1e-9).all()
 assert (abs(check.K-check.prefix)<1e-9).all()
 assert (abs(check['mean_x']-check['mean_y'])<1e-9).all()
 result={'status':'PASS','original_pairlevel_rows':len(p),'primary_historical_runs':len(hist),'fully_resolved_runs':len(completed),'better_pair_mean_runs':len(improved),'mean_better_module_count_worse':26,'mean_better_full_prefix_worse':40,'joint_dominated_any_positive_additive_weight':len(dual),'joint_dominated_unique_brazilian_plants':dual.target_id.nunique(),'wrong_accepted_signs_in_joint_dominated':int(dual.wrong.sum()),'example':{'target':'D09_PS_001','mean_local':285/36,'mean_albuquerque':258/36,'max_local':14,'max_albuquerque':15,'module_local':100,'module_albuquerque':102},'source_validation':'Direct vectorized graph endpoint reconstruction; matched explicit-loop cost workbook 188/188','metrological_test':'NOT MEASURED'}
 Path(out).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 return result
if __name__=='__main__':
 verify(sys.argv[1],sys.argv[2])
