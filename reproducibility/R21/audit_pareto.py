import pandas as pd, numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
m=pd.read_csv(P/'R15_TASK_METRICS_PRIMARY38.csv')
dims=['mean_pair_cells','winner_depth','K_all','N_mod_cell']
r=[]
for target,g in m.groupby('target_id',sort=False):
    assert len(g)==6
    good=g[(g['winner_correct'])&(g['fully_resolved'])].copy()
    bad=g[~((g['winner_correct'])&(g['fully_resolved']))]
    vals=good[dims].to_numpy(dtype=float)
    dom=np.zeros(len(good),dtype=bool); dom_by=[[] for _ in range(len(good))]
    for i in range(len(good)):
      for j in range(len(good)):
        if j==i:continue
        if np.all(vals[j]<=vals[i]) and np.any(vals[j]<vals[i]):
          dom[i]=True;dom_by[i].append(good.iloc[j].source_order)
    good['pareto_dom']=dom
    good['dominated_by']=[';'.join(x) for x in dom_by]
    good['n_correct_complete_candidates']=len(good)
    good['target_id']=target
    r.extend(good[['target_id','source_order','pareto_dom','dominated_by','n_correct_complete_candidates']+dims].to_dict('records'))
rr=pd.DataFrame(r)
rr.to_csv(P/'Pareto_EligibleOrder_Census.csv',index=False)
front=rr.loc[~rr.pareto_dom]
per_target=front.groupby('target_id').size()
local=rr[rr.source_order.eq('Target-local heuristic')]
print({'total_correct_complete_candidates':len(rr),'pareto_unique_orders':len(front),'mean_per_target_front_size':float(per_target.mean()),'min':int(per_target.min()),'max':int(per_target.max()),'targets_with_one_pareto':int((per_target==1).sum()),'targets_with_multiple_pareto':int((per_target>1).sum()),'local_non_dominated':int((~local.pareto_dom).sum()),'local_dominated':int(local.pareto_dom.sum()),'historical_pareto':int((front.source_order!='Target-local heuristic').sum()),'source_counts':front.source_order.value_counts().to_dict()})
print('per-target fronts',per_target.value_counts().sort_index().to_dict())
print('local dominated examples',local.loc[local.pareto_dom,['target_id','dominated_by']].head(12).to_string(index=False))
