#!/usr/bin/env python3
"""Independent reconstruction of Project66 source-locked pairwise graph metrics.
Uses original R15 per-pair derived observations rather than manuscript aggregate values.
This is a retrospective derived-record audit, not physical metrology verification.
"""
import csv, hashlib, json, math
from collections import defaultdict, Counter
from pathlib import Path

P=Path(__file__).resolve().parent
pair_path=P/'external_pairlevel_decisions.csv'
metric_path=P/'R15_TASK_METRICS_PRIMARY38.csv'
assert hashlib.sha256(pair_path.read_bytes()).hexdigest()=='d742769b8874dceb63b8aef7bf00b712097d1d598beb0588b0d706c7278f4c68'
assert hashlib.sha256(metric_path.read_bytes()).hexdigest()=='bfc337ea2ffd16dfa69f0b6745fe0480c3fc46556ad45c45bd7ddf9ea3ef03d2'
with pair_path.open(newline='') as f: pair_rows=list(csv.DictReader(f))
with metric_path.open(newline='') as f: met_rows=list(csv.DictReader(f))
assert len(pair_rows)==32400 and len(met_rows)==228
pairs=defaultdict(list)
for r in pair_rows:pairs[(r['target_id'],r['source_order'])].append(r)
for group,rs in pairs.items():
 assert len(rs)==36 and len({(r['module_a'],r['module_b']) for r in rs})==36
out=[]; failures=[]
for record in met_rows:
 target=record['target_id']; order=record['source_order']; rows=pairs[(target,order)]
 mods={r['module_a'] for r in rows}|{r['module_b'] for r in rows}; assert len(mods)==9
 fullwins=Counter();acceptedwins=Counter();depths={}; pairs_good={}
 for r in rows:
  a,b=r['module_a'],r['module_b'];full=float(r['full_target_normalized_difference']);assert math.isfinite(full) and full!=0
  winner=a if full>0 else b
  fullwins[winner]+=1
  k=r['stop_cells']; und=r['unresolved']=='True'; wrong=r['wrong_accepted']=='True'
  assert (not k)==und
  if und:
   assert not wrong
   depths[(a,b)]=None
  else:
   k=int(float(k)); assert k>=1
   accepted=(b if winner==a else a) if wrong else winner
   acceptedwins[accepted]+=1
   depths[(a,b)]=k
   pairs_good[(a,b)]=not wrong
 fullchamp=[x for x in mods if fullwins[x]==8]
 assert len(fullchamp)==1
 w=fullchamp[0]
 achamps=[x for x in mods if acceptedwins[x]==8]
 assert len(achamps)<=1
 aw=achamps[0] if achamps else None
 assert record['true_winner']==w
 assert record['accepted_condorcet_winner']==(aw if aw is not None else '')
 assert (record['winner_certified']=='True')==(aw is not None)
 assert (record['winner_correct']=='True')==(aw==w)
 assert int(record['n_wrong'])==sum(r['wrong_accepted']=='True' for r in rows)
 assert int(record['n_unresolved'])==sum(r['unresolved']=='True' for r in rows)
 allresolved=all(x is not None for x in depths.values());assert (record['fully_resolved']=='True')==allresolved
 if allresolved:
  ks=list(depths.values());kmean=sum(ks)/36; kmax=max(ks)
  vertexlast={v:max(k for (a,b),k in depths.items() if v in (a,b)) for v in mods}
  nmod=sum(vertexlast.values())
  for actual,field in [(kmean,'mean_pair_cells'),(kmax,'K_all'),(nmod,'N_mod_cell')]:
   assert abs(actual-float(record[field]))<1e-9,(target,order,field,actual,record[field])
 if aw:
  star=tuple(k for (a,b),k in depths.items() if aw in (a,b))
  if all(k is not None for k in star):
   assert max(star)==int(float(record['winner_depth']))
  else: raise AssertionError('Certified winner with unresolved incident edge')
 if aw==w:
  true_star=tuple(k for (a,b),k in depths.items() if w in (a,b))
  assert all(k is not None for k in true_star)
  assert max(true_star)==int(float(record['true_winner_depth']))
 out.append({'target_id':target,'source_order':order,'full_winner':w,'accepted_winner':aw,'correct':aw==w,'complete':allresolved})
assert len(out)==228
s=Counter((x['complete'],x['correct']) for x in out)
assert s[(True,True)]==222 and s[(True,False)]==4 and s[(False,True)]==2
assert len({x['target_id'] for x in out})==38
summary={'status':'PASS','source_pair_rows':len(pair_rows),'source_all_target_order_groups':len(pairs),'audited_primary_order_records':len(out),'complete_correct':s[(True,True)],'complete_incorrect':s[(True,False)],'incomplete_correct':s[(False,True)],'primary_target_count':38,'all_recomputed_metric_checks':'PASS','raw_physical_validation':False}
(P/'Independent_Graph_Source_Verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
