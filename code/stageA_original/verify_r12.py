from pathlib import Path
import json, math
import pandas as pd
ROOT=Path(__file__).resolve().parent
O=ROOT/'outputs/r12_directional'
full=pd.read_csv(O/'transfer_5x5_full.csv')
port=pd.read_csv(O/'source_portfolio_5site.csv')
common=pd.read_csv(O/'source_portfolio_common5.csv')
pool=pd.read_csv(O/'pooled_loco5.csv')
sign=pd.read_csv(O/'sign_agreement_pairs.csv')
summary=json.loads((O/'summary_5site.json').read_text())
checks=[]
def ck(name,cond):
    checks.append((name,bool(cond)))
def val(src,tgt): return float(full.query('source_order==@src and target_site==@tgt').excess_pct.iloc[0])
def pval(src,col): return float(port.query('source_order==@src')[col].iloc[0])
def cval(src,col): return float(common.query('source_order==@src')[col].iloc[0])
ck('25 transfer cells',len(full)==25)
ck('all aggregate unresolved zero',int(full.unresolved_pairs.sum())==0)
ck('all aggregate wrong accepted zero',int(full.wrong_accepted_pairs.sum())==0)
ck('locked Eugene->Cocoa',abs(val('Eugene','Cocoa')-45.94594594594595)<1e-12)
ck('locked Eugene->Golden',abs(val('Eugene','Golden')-57.75075987841945)<1e-12)
ck('locked Eugene->Switzerland',abs(val('Eugene','Switzerland')-60.47297297297298)<1e-12)
ck('locked Eugene->Albuquerque',abs(val('Eugene','Albuquerque')-68.83116883116884)<1e-12)
ck('new Albuquerque->Switzerland',abs(val('Albuquerque','Switzerland')+1.3513513513513487)<1e-12)
ck('new Golden->Switzerland',abs(val('Golden','Switzerland')-2.3648648648648685)<1e-12)
ck('Albuquerque off-target mean',abs(pval('Albuquerque','mean_offtarget_excess_pct')+0.19166692779327144)<1e-12)
ck('Eugene off-target mean',abs(pval('Eugene','mean_offtarget_excess_pct')-58.25021190712681)<1e-12)
ck('Albuquerque common5 mean',abs(cval('Albuquerque','common5_mean_offtarget_excess_pct')+0.9998966515088831)<1e-12)
ck('Albuquerque common5 worst zero',abs(cval('Albuquerque','common5_worst_pct'))<1e-12)
pg=pool.query("sequence=='GlobalPooled5'")
ck('GlobalPooled5 mean',abs(float(pg.excess_pct.mean())-5.6110036621113695)<1e-12)
ck('GlobalPooled5 worst',abs(float(pg.excess_pct.max())-11.363636363636376)<1e-12)
ck('Switzerland source files 12',len(summary['switzerland_source_files'])==12)
ck('sign pair rows 10',len(sign)==10)
failed=[n for n,c in checks if not c]
for n,c in checks: print(('PASS' if c else 'FAIL'),n)
print(f'{sum(c for _,c in checks)}/{len(checks)} checks PASS')
if failed: raise SystemExit('FAILED: '+', '.join(failed))
