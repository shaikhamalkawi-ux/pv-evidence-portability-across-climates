#!/usr/bin/env python3
"""Frozen-ledger, deterministic descriptive census for R18. No new PV source measurements.

Inputs: exact R16 full-pair census and exact R16 primary comparison ledger.
Output: 12-case detail and magnitude summary; asserts the preregistered frozen counts.
"""
from __future__ import annotations
import csv, hashlib, json
from decimal import Decimal
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
C=P/'R16_COMPLETE_VALIDITY_GATED_CENSUS.csv'
L=P/'R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(p):
    with p.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))
rows=read(C); ledger=read(L)
assert len(rows)==len(ledger)==190
keys=lambda r: (r['target_id'],r['source_order'])
lut={keys(r):r for r in ledger}
assert len(lut)==190
assert len(set(map(keys,rows)))==190
valid=[]; raw=[]; bad=[]; excluded=[]
for c in rows:
    l=lut[keys(c)]
    assert c['source_winner_correct']==l['source_winner_correct']
    complete=c['all_pairs_complete']=='True'; correct=c['source_winner_correct']=='True'
    assert c['all_pairs_complete'] in ('True','False') and c['source_winner_correct'] in ('True','False')
    if not complete:
        excluded.append(keys(c));continue
    a=Decimal(l['delta_mean_pair_cells']); b=Decimal(l['delta_winner_depth'])
    is_reverse=(a<0 and b>0) or (a>0 and b<0)
    assert (c['classification']=='strict_reversal')==is_reverse
    if is_reverse:
        raw.append(keys(c))
        (valid if correct else bad).append((c,l))
assert len(raw)==16 and len(valid)==12 and len(bad)==4 and len(excluded)==2
assert sorted(k for c,k in bad for k in [keys(c)])==sorted([('2019_System_2B',q) for q in ['Cocoa','Golden','Switzerland','Albuquerque']])
assert len({c['target_id'] for c,l in valid})==11
out=[]
for c,l in valid:
    target=l['target_id']
    band='Brazil' if target.startswith('D09_') else 'Italy' if target.startswith('D24_') else 'Germany' if target.startswith('201') else 'Other'
    assert band!='Other'
    dmean=Decimal(l['pct_mean_pair_cells']);dwin=Decimal(l['delta_winner_depth'])
    assert abs(dmean)<Decimal(5)
    out.append(dict(source_family=band, target_id=target,source_order=l['source_order'],
       delta_pair_mean_percent=l['pct_mean_pair_cells'],
       delta_winner_depth_cells=l['delta_winner_depth'],
       delta_K_all_cells=l['delta_K_all'],delta_N_mod_cell=l['delta_N_mod_cell'],
       winner_correct=c['source_winner_correct'], all_pairs_complete=c['all_pairs_complete']))
assert sum(r['source_family']=='Brazil' for r in out)==9
assert sum(abs(Decimal(r['delta_winner_depth_cells']))==1 for r in out)==9
assert Counter(r['source_family'] for r in out)=={'Brazil':9,'Germany':2,'Italy':1}
with (P/'R18_VALIDITY_GATED_12_CASE_MAGNITUDES.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
result=dict(status='PASS',input_rows=190,complete_pairs=188,correct_complete=184,raw_reversals=16,
    incorrect_apparent_reversals=4,valid_reversals=12,distinct_targets=11,
    source_family_breakdown={'Brazil':9,'Germany':2,'Italy':1},
    one_cell_absolute_winner_depth=9,all_abs_pair_mean_percent_lt_5=True,
    max_abs_pair_mean_percent=str(max(abs(Decimal(r['delta_pair_mean_percent'])) for r in out)),
    source_sha256={C.name:sha(C),L.name:sha(L)},
    notes='Finite, dependent, retrospective replays; not independent site or population inference.')
(P/'R18_MAGNITUDE_QA.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
