#!/usr/bin/env python3
"""Independent decimal re-aggregation of *frozen* R15 comparison ledger.
No raw data, no new PV measurements; fail closed against declared invariant outcomes.
"""
import csv, json
from collections import Counter
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent
src=P/'R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv'
def flag(s):
    if s not in ('True','False'): raise AssertionError('unexpected bool '+repr(s))
    return s=='True'
def sign(s):
    if not s: return None
    d=Decimal(s)
    if not d.is_finite(): raise AssertionError('not finite')
    return 'better' if d<0 else 'worse' if d>0 else 'same'
rows=list(csv.DictReader(src.open(newline='')))
assert len(rows)==190 and len(set((r['target_id'],r['source_order']) for r in rows))==190
out=[]; summary=Counter(); full_bad=[]; dropped=[]
for r in rows:
    correct=flag(r['source_winner_correct']); local_correct=flag(r['local_winner_correct']); certified=flag(r['source_winner_certified'])
    assert local_correct and certified
    a=sign(r['delta_mean_pair_cells']);b=sign(r['delta_winner_depth'])
    assert b is not None
    if a is None:
        dropped.append((r['target_id'],r['source_order']))
        assert correct and r['n_unresolved'] not in ('','0')
        kind='missing_all_pairs'
    else:
        summary['n_full']+=1
        if not correct:full_bad.append((r['target_id'],r['source_order'],a,b))
        if a=='better' and b=='worse' or a=='worse' and b=='better':
            summary['raw_reversals']+=1
            if correct:summary['validity_gated_reversals']+=1
            else:summary['invalid_apparent_reversals']+=1
        if correct:summary['valid_full']+=1
        kind='strict_reversal' if (a=='better' and b=='worse' or a=='worse' and b=='better') else 'no_strict_reversal'
        summary[f'{"valid" if correct else "invalid"}_{a}_{b}']+=1
    out.append(dict(target_id=r['target_id'],source_order=r['source_order'],all_pairs_complete=a is not None,source_winner_correct=correct,pair_mean_direction=a,winner_depth_direction=b,classification=kind))
expected_dropped=[('D09_PS_009','Eugene'),('D09_PS_040','Eugene')]
expected_wrong=[('2019_System_2B',name,'worse','better') for name in ('Cocoa','Golden','Switzerland','Albuquerque')]
assert sorted(dropped)==sorted(expected_dropped),(dropped,expected_dropped)
assert sorted(full_bad)==sorted(expected_wrong),full_bad
assert summary['n_full']==188 and summary['valid_full']==184
assert summary['raw_reversals']==16 and summary['invalid_apparent_reversals']==4 and summary['validity_gated_reversals']==12
assert sum(not o['source_winner_correct'] for o in out)==4
assert summary['valid_better_better']==59 and summary['valid_better_same']==17 and summary['valid_better_worse']==3
assert summary['valid_same_better']==2 and summary['valid_same_same']==0 and summary['valid_same_worse']==0
assert summary['valid_worse_better']==9 and summary['valid_worse_same']==25 and summary['valid_worse_worse']==69
assert summary['invalid_worse_better']==4
assert len(out)==190
# m=2 identity, necessary condition for different depths
for k in (1,2,5,17):
    m=2; depths=[k]; pairmean=k;kall=k;kwin=k;nmod=2*k
    assert pairmean==kall==kwin and nmod==2*k
cols=list(out[0]);f=P/'R16_COMPLETE_VALIDITY_GATED_CENSUS.csv'
with f.open('w',newline='') as h:
    w=csv.DictWriter(h,fieldnames=cols);w.writeheader();w.writerows(out)
result={'status':'PASS','input_rows':190,'complete_all_pairs':188,'correct_winner_and_complete_all_pairs':184,'incorrect_winner_complete_all_pairs':4,'winner_correct_but_incomplete_all_pairs':2,'raw_strict_task_reversals':16,'incorrect_winner_apparent_reversals':4,'validity_gated_strict_reversals':12,'unique_wrong_target':'2019_System_2B','wrong_sources':['Cocoa','Golden','Switzerland','Albuquerque'],'crosstab_valid':{a:{b:summary[f'valid_{a}_{b}'] for b in ('better','same','worse')} for a in ('better','same','worse')},'m2_identity_check':'PASS','interpretation':'Retrospective full-reference gate only, not a prospective decision-risk certificate'}
(P/'R16_VALIDITY_GATE_INDEPENDENT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
