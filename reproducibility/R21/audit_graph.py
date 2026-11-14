import numpy as np, pandas as pd
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
pairs=pd.read_csv(P/'external_pairlevel_decisions.csv')
metrics=pd.read_csv(P/'R15_TASK_METRICS_PRIMARY38.csv')
comp=pd.read_csv(P/'R15_TASK_COMPARISONS_PRIMARY38.csv')
assert len(pairs)==32400 and len(metrics)==228 and len(comp)==190
ids=list(comp.target_id.unique());assert len(ids)==38
pmap={(tid,ord):df for (tid,ord),df in pairs.groupby(['target_id','source_order'])}
mmap={(r.target_id,r.source_order):r for r in metrics.itertuples(index=False)}
results=[];errs=[]
for c in comp.itertuples(index=False):
 key=(c.target_id,c.source_order)
 s=pmap[key].sort_values(['module_a','module_b']).reset_index(drop=True)
 t=pmap[(c.target_id,'Target-local heuristic')].sort_values(['module_a','module_b']).reset_index(drop=True)
 assert np.array_equal(s[['module_a','module_b']].values,t[['module_a','module_b']].values)
 sc=mmap[key];lo=mmap[(c.target_id,'Target-local heuristic')]
 assert sc.true_winner==lo.true_winner
 winner=sc.true_winner
 if sc.fully_resolved:
  assert len(s)==len(t)==36 and s.stop_cells.notna().all() and t.stop_cells.notna().all()
  raw_s=s.stop_cells.to_numpy();raw_t=t.stop_cells.to_numpy(); dd=raw_s-raw_t
  incidence=(s.module_a.eq(winner)|s.module_b.eq(winner)).to_numpy()
  assert incidence.sum()==8 and (~incidence).sum()==28
  swmax=raw_s[incidence].max(); lwmax=raw_t[incidence].max()
  sallmax=raw_s.max();lallmax=raw_t.max()
  if sc.winner_correct:
   assert abs(swmax-sc.true_winner_depth)<1e-8
   assert abs(swmax-sc.winner_depth)<1e-8
  assert abs(lwmax-lo.true_winner_depth)<1e-8
  assert abs(raw_s.mean()-c.source_mean_pair_cells)<1e-8
  assert abs(raw_t.mean()-c.local_mean_pair_cells)<1e-8
  assert abs(sallmax-c.source_K_all)<1e-8
  assert abs(lallmax-c.local_K_all)<1e-8
  assert abs(dd.sum()/36-c.delta_mean_pair_cells)<1e-8
  assert sc.winner_correct==c.source_winner_correct
  assert lo.winner_correct
  # winner's incident edge threshold vs non-winner bottleneck
  slmax=raw_s[~incidence].max();llmax=raw_t[~incidence].max()
  source_nonwin_critical=np.flatnonzero((~incidence)&(raw_s==sallmax));
  source_winner_critical=np.flatnonzero(incidence&(raw_s==sallmax));
  local_nonwin_critical=np.flatnonzero((~incidence)&(raw_t==lallmax));
  delta_star=float(dd[incidence].sum());delta_other=float(dd[~incidence].sum());
  edge_better=int((dd<0).sum());edge_worse=int((dd>0).sum());edge_same=int((dd==0).sum());
  stage_ab={'target_id':c.target_id,'source_order':c.source_order,
   'correct_and_complete':bool(sc.winner_correct),'source_winner':winner,'local_winner':lo.true_winner,
   'delta_mean':float(c.delta_mean_pair_cells),'delta_Kwin':float(c.delta_winner_depth),
   'delta_Kall':float(c.delta_K_all),'delta_N_mod_cell':float(c.delta_N_mod_cell),
   'delta_star_edge_sum':delta_star,'delta_other_edge_sum':delta_other,
   'delta_star_avg':delta_star/8,'delta_other_avg':delta_other/28,
   'star_share_of_mean_delta':delta_star/dd.sum() if dd.sum() else np.nan,
   'winner_star_bottleneck_source':swmax,'winner_star_bottleneck_local':lwmax,
   'nonwinner_bottleneck_source':slmax,'nonwinner_bottleneck_local':llmax,
   'source_all_critical_winner_incident':len(source_winner_critical)>0,
   'local_all_critical_winner_incident':len(np.flatnonzero(incidence & (raw_t==lallmax)))>0,
   'source_critical_nonwinner_count':len(source_nonwin_critical),
   'local_critical_nonwinner_count':len(local_nonwin_critical),
   'source_gap_Kall_minus_Kwin':sallmax-swmax,'local_gap_Kall_minus_Kwin':lallmax-lwmax,
   'delta_gap':(sallmax-swmax)-(lallmax-lwmax),
   'edge_improved':edge_better,'edge_worsened':edge_worse,'edge_tied':edge_same,
   'edge_componentwise_dominance_source':edge_worse==0 and edge_better>0,
   'edge_componentwise_dominance_local':edge_better==0 and edge_worse>0,
   'source_star_changes_better':int((dd[incidence]<0).sum()),
   'source_star_changes_worse':int((dd[incidence]>0).sum()),
   'source_nonstar_changes_better':int((dd[~incidence]<0).sum()),
   'source_nonstar_changes_worse':int((dd[~incidence]>0).sum()),
  }
  results.append(stage_ab)
 else:
  assert not c.n_unresolved==0
res=pd.DataFrame(results)
assert len(res)==188
valid=res[res.correct_and_complete].copy();assert len(valid)==184
rev=valid[((valid.delta_mean>0)&(valid.delta_Kwin<0)) | ((valid.delta_mean<0)&(valid.delta_Kwin>0))].copy(); assert len(rev)==12
allimprove=valid[valid.delta_mean<0].copy(); assert len(allimprove)==79
res.to_csv(P/'Graph_Complete188.csv',index=False)
rev.to_csv(P/'Graph_12ValidReversals.csv',index=False)

print('ALL',len(res),'valid',len(valid),'reversal',len(rev),'mean improve',len(allimprove))
print('12 rev by source',Counter('Germany' if x.startswith('201') else 'Italy' if x.startswith('D24') else 'Brazil' for x in rev.target_id))
print('gap summary valid source:',valid.source_gap_Kall_minus_Kwin.describe().to_dict(),'local:',valid.local_gap_Kall_minus_Kwin.describe().to_dict())
print('gap statuses source',valid.source_gap_Kall_minus_Kwin.gt(0).sum(),'local',valid.local_gap_Kall_minus_Kwin.gt(0).sum())
print('12 detail');print(rev[['target_id','source_order','delta_mean','delta_Kwin','delta_Kall','delta_star_edge_sum','delta_other_edge_sum','source_gap_Kall_minus_Kwin','local_gap_Kall_minus_Kwin','delta_gap','edge_improved','edge_worsened','source_star_changes_better','source_star_changes_worse']].to_string(index=False))
print('12 sums star vs other',{'nonstar_positive':int((rev.delta_other_edge_sum>0).sum()),'star_positive':int((rev.delta_star_edge_sum>0).sum()),'star_negative':int((rev.delta_star_edge_sum<0).sum()),'nonstar_negative':int((rev.delta_other_edge_sum<0).sum()),'gap_increase':int((rev.delta_gap>0).sum()),'gap_decrease':int((rev.delta_gap<0).sum())})
print('componentwise dominance source better',valid.edge_componentwise_dominance_source.sum(),'local better',valid.edge_componentwise_dominance_local.sum(), 'mixed', ((valid.edge_worsened>0)&(valid.edge_improved>0)).sum())
print('79 mixed edge',int(((allimprove.edge_worsened>0)&(allimprove.edge_improved>0)).sum()),'source componentwise dom',allimprove.edge_componentwise_dominance_source.sum())
print('star mean/losses 12 directional');print(rev.groupby([rev.delta_mean.gt(0).map({True:'mean worse',False:'mean better'}),rev.delta_Kwin.gt(0).map({True:'winner later',False:'winner earlier'})])[[ 'delta_star_edge_sum','delta_other_edge_sum','delta_gap']].agg(['mean','min','max']).to_string())
