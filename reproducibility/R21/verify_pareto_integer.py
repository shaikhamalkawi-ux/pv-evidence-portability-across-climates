#!/usr/bin/env python3
"""Integer, pair-row-only independent Pareto check for R15 primary 38 targets.
No posthoc eligibility is available to a prospective user; this is interpretation only.
"""
import csv, hashlib, json
from collections import defaultdict, Counter
from pathlib import Path
P=Path(__file__).resolve().parent
f=P/'external_pairlevel_decisions.csv'
assert hashlib.sha256(f.read_bytes()).hexdigest()=='d742769b8874dceb63b8aef7bf00b712097d1d598beb0588b0d706c7278f4c68'
raw=defaultdict(list)
with f.open(newline='') as fd:
 for row in csv.DictReader(fd): raw[(row['target_id'],row['source_order'])].append(row)
comp_path=P/'R15_TASK_COMPARISONS_PRIMARY38.csv'
assert hashlib.sha256(comp_path.read_bytes()).hexdigest()=='45060d415faa8ed84f5b1212a36893e2401913616031deddf73e244d43bb3c9d'
with comp_path.open(newline='') as fd:primary=sorted({r['target_id'] for r in csv.DictReader(fd)})
assert len(primary)==38
orders=['Target-local heuristic','Cocoa','Eugene','Golden','Switzerland','Albuquerque']
metrics=[]
for target in primary:
 for source in orders:
  rs=raw[(target,source)];assert len(rs)==36
  if any(x['unresolved']=='True' for x in rs) or any(x['wrong_accepted']=='True' for x in rs): continue
  fullwin=Counter()
  for x in rs:
   a,b=x['module_a'],x['module_b']
   winner=a if float(x['full_target_normalized_difference'])>0 else b
   fullwin[winner]+=1
  winner=next(w for w in fullwin if fullwin[w]==8)
  depths={(r['module_a'],r['module_b']):int(float(r['stop_cells'])) for r in rs}
  allk=max(depths.values()); star=max(k for (a,b),k in depths.items() if winner in (a,b));mods={v for e in depths for v in e}
  n=sum(max(k for (a,b),k in depths.items() if v in (a,b)) for v in mods)
  metrics.append((target,source,(sum(depths.values()),star,allk,n)))
assert len(metrics)==222
front=[]
for target in primary:
 choices=[(source,cost) for site,source,cost in metrics if site==target]
 for source,cost in choices:
  dominated=any(all(a<=b for a,b in zip(other,cost)) and any(a<b for a,b in zip(other,cost)) for s,other in choices if s!=source)
  if not dominated:front.append((target,source,cost))
front_counts=Counter(x[0] for x in front)
local=set(x[0] for x in front if x[1]=='Target-local heuristic')
summary={'status':'PASS','source':'R15 32400 pair records; exact integer depth arithmetic','eligible_target_order_records':len(metrics),'eligible_historical':len(metrics)-38,'pareto_nondominated_records':len(front),'targets_with_multiple_distinct_tradeoff_options':sum(n>1 for n in front_counts.values()),'targets_with_local_dominated':38-len(local),'local_non_dominated':len(local),'targets_with_front_sizes':dict(sorted(Counter(front_counts.values()).items()))}
assert len(front)==74 and summary['targets_with_multiple_distinct_tradeoff_options']==23 and summary['targets_with_local_dominated']==16
(P/'Independent_Pareto_Integer_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
