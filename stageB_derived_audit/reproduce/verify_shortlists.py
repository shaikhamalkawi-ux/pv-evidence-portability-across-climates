#!/usr/bin/env python3
"""Recalculate the exact-unit Stage-B comparison from the manuscript's 11-row table.

Source: W. Marion et al. (2014), Solar Energy 110, 736–744,
DOI 10.1016/j.solener.2014.10.017. These are published annual
final-yield TABLE VALUES, not redistributions of time-series data.
No performance inference or uncertainty is added.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'results/exact_unit_cocoa_eugene_final_yield.csv'
rows=list(csv.DictReader(P.open()))
assert len(rows)==11 and len({r['physical_module_id'] for r in rows})==11
names=('cocoa','eugene')
vals={s:{r['physical_module_id']:float(r[f'{s}_final_yield_hours']) for r in rows} for s in names}
best={s:max(v.values()) for s,v in vals.items()}
def deficit(s,m): return 100*(1-vals[s][m]/best[s])
def eligible(s,q):return {m for m in vals[s] if deficit(s,m)<=q+1e-12}
assert best=={'cocoa':2019.0,'eugene':1482.0}
q=5.0
sc,st=eligible('cocoa',q),eligible('eugene',q)
false=st-sc
assert len(sc)==2 and len(st)==5 and len(false)==3 and len(st&sc)==2
assert false=={'aSiTriple28324','HIT05667','aSiTandem72-46'}
reverse=eligible('cocoa',q)-eligible('eugene',q)
assert not reverse
intervals={m:(deficit('eugene',m),deficit('cocoa',m)) for m in vals['cocoa'] if deficit('eugene',m)<deficit('cocoa',m)}
assert len(intervals)==10
assert abs(intervals['HIT05667'][0]-3.239)<.001
assert abs(intervals['HIT05667'][1]-8.123)<.001
assert round(len(sc&st)/len(st),2)==.4
print('STAGE B VERIFIED: 11 unique exact physical units, Cocoa 2, Eugene 5, false excluded 3, target coverage 40%, nonempty forward intervals 10, reverse intervals 0')
