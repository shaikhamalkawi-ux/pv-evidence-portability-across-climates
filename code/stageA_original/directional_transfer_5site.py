from pathlib import Path
import itertools,re,json,hashlib,math,argparse
import numpy as np,pandas as pd
from scipy.spatial import Delaunay
from scipy.stats import spearmanr, pearsonr
from scipy.optimize import linprog
import h5py

ROOT=Path(__file__).resolve().parent
MAT=ROOT/'data/sandia_iec61853_performance_matrix_long.csv'
SLIM=ROOT/'mpert_core'
parser=argparse.ArgumentParser(description='Paper 1 R12 five-site directional characterization-order audit')
parser.add_argument('--task13-dir', required=True, help='Directory containing the 12 public IEA_Task13_YYYY_MM.csv files')
parser.add_argument('--albuquerque-nc', required=True, help='Path to the public Sandia tmod_sample_data.nc source')
parser.add_argument('--output-dir', default=str(ROOT/'outputs/r12_reproduced'))
args=parser.parse_args()
SWDIR=Path(args.task13_dir).expanduser().resolve()
NC=Path(args.albuquerque_nc).expanduser().resolve()
OUT=Path(args.output_dir).expanduser().resolve(); OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_NC_SHA256='a934d40671063ee2a8666ee133c612390f7f1a339549fdc77159b81efdd5abd7'
actual_nc_sha256=hashlib.sha256(NC.read_bytes()).hexdigest()
if actual_nc_sha256 != EXPECTED_NC_SHA256:
    raise ValueError(f'Unexpected Albuquerque source SHA-256: {actual_nc_sha256}')
months=sorted(SWDIR.glob('IEA_Task13_20??_??.csv'))
if len(months)!=12:
    raise SystemExit(f'Expected 12 Task13 monthly CSVs in {SWDIR}, found {len(months)}')

mat=pd.read_csv(MAT); mods=sorted(mat.module_id.unique())
coords=mat[['irradiance_Wm2','temperature_C']].drop_duplicates().sort_values(['irradiance_Wm2','temperature_C']).reset_index(drop=True)
xy=coords[['irradiance_Wm2','temperature_C']].to_numpy(float); tri=Delaunay(xy)
Z=np.empty((len(mods),len(xy)))
for ii,m in enumerate(mods):
    mm=coords.merge(mat[mat.module_id==m],on=['irradiance_Wm2','temperature_C'],how='left')
    pstc=float(mm.loc[(mm.irradiance_Wm2==1000)&(mm.temperature_C==25),'Pmp_W'].iloc[0]); Z[ii]=mm.Pmp_W.to_numpy(float)/pstc
stc=int(coords.index[(coords.irradiance_Wm2==1000)&(coords.temperature_C==25)][0])

def bary_weights(q,simplex_keep=None):
    q=np.asarray(q,float); sid=tri.find_simplex(q); inside=sid>=0
    if simplex_keep is not None: inside &= np.isin(sid,list(simplex_keep))
    qq=q[inside]; ss=sid[inside]
    if len(qq)==0: raise ValueError('No retained points')
    T=tri.transform[ss,:2,:]; r=qq-tri.transform[ss,2,:]
    b12=np.einsum('nij,nj->ni',T,r); bary=np.c_[b12,1-b12.sum(axis=1)]
    verts=tri.simplices[ss]
    w=np.zeros(len(xy),float)
    for k in range(3): w += np.bincount(verts[:,k],weights=bary[:,k],minlength=len(xy))
    w/=len(qq)
    return w,inside,sid

# Core US records and weights
recs={}; site_simplexes={s:[] for s in ['Cocoa','Eugene','Golden']}
for fp in sorted(SLIM.glob('*.csv')):
    m=re.match(r'(Cocoa|Eugene|Golden)_(.+?)(\d+)\.csv',fp.name); site,tech,mid=m.groups()
    df=pd.read_csv(fp,usecols=['poa','tmod','pmp'])
    for c in ['poa','tmod','pmp']:
        df[c]=pd.to_numeric(df[c],errors='coerce'); df.loc[df[c]<=-9000,c]=np.nan
    valid=df.poa.notna()&df.tmod.notna()&df.pmp.notna()&(df.poa>0)&(df.pmp>=0)
    q=df.loc[valid,['poa','tmod']].to_numpy(float); sid=tri.find_simplex(q); keep=sid>=0
    q=q[keep]; sid=sid[keep]
    recs[(site,tech,mid)]=(q,sid); site_simplexes[site].append(sid)
site_w={}; site_sets={}
for site in ['Cocoa','Eugene','Golden']:
    ws=[]
    for (s,tech,mid),(q,sid) in recs.items():
        if s==site: ws.append(bary_weights(q)[0])
    site_w[site]=np.mean(np.vstack(ws),axis=0)
    site_sets[site]=set(np.unique(np.concatenate(site_simplexes[site])).tolist())

# Switzerland
frames=[]; src_hash=[]
for fp in months:
    df=pd.read_csv(fp,sep=';'); df.columns=[c.strip() for c in df.columns]
    for c in ['Pm','Tbom','Gpoa']: df[c]=pd.to_numeric(df[c],errors='coerce')
    frames.append(df[['Pm','Tbom','Gpoa']]); src_hash.append((fp.name,hashlib.sha256(fp.read_bytes()).hexdigest(),len(df)))
sw=pd.concat(frames,ignore_index=True); valid=sw[['Pm','Tbom','Gpoa']].notna().all(axis=1)&(sw.Gpoa>0)&(sw.Pm>=0)
qv=sw.loc[valid,['Gpoa','Tbom']].to_numpy(float); sid=tri.find_simplex(qv); inside=sid>=0
q_sw=qv[inside]; sid_sw=sid[inside]; site_w['Switzerland']=bary_weights(q_sw)[0]; site_sets['Switzerland']=set(np.unique(sid_sw).tolist())

# Albuquerque 5min
with h5py.File(NC,'r') as f:
    t=np.asarray(f['time'][:],dtype=np.int64); poa=np.asarray(f['poa_global'][:],float); tp=np.asarray(f['temp_pv'][:],float); positions=np.asarray(f['position'][:],int)
idx1=int(np.where(positions==1)[0][0]); idx4=int(np.where(positions==4)[0][0])
tmod=np.nanmean(tp[:,[idx1,idx4]],axis=1); time=pd.Timestamp('2020-01-01')+pd.to_timedelta(t,unit='m')
raw=pd.DataFrame({'time':time,'poa':poa,'tmod':tmod}).set_index('time'); five=raw.resample('5min').mean(numeric_only=True)
v=five[['poa','tmod']].notna().all(axis=1)&(five.poa>10.0); qab0=five.loc[v,['poa','tmod']].to_numpy(float); sid=tri.find_simplex(qab0); inside=sid>=0
q_abq=qab0[inside]; sid_abq=sid[inside]; site_w['Albuquerque']=bary_weights(q_abq)[0]; site_sets['Albuquerque']=set(np.unique(sid_abq).tolist())

sites=['Cocoa','Eugene','Golden','Switzerland','Albuquerque']

pairs=list(itertools.combinations(range(len(mods)),2)); pidx={p:i for i,p in enumerate(pairs)}; NP=len(pairs)
def pair_struct(w):
    contrib=np.vstack([w*(Z[a]-Z[b]) for a,b in pairs]); fd=contrib.sum(axis=1); cal=[]
    for a,b in pairs:
        retained=[i for i in range(len(mods)) if i not in {a,b}]
        cal.append(np.array([pidx[(x,y)] for x,y in itertools.combinations(retained,2)],int))
    return contrib,fd,cal

def make_order(w):
    elig=[j for j in range(len(xy)) if j!=stc and w[j]>1e-14]
    return np.array(sorted(elig,key=lambda j:(-w[j],xy[j,0],xy[j,1])),int)
def eval_order(w,order):
    contrib,fd,cal=pair_struct(w); cum=np.cumsum(contrib[:,order],axis=1)
    stop=np.full(NP,np.nan); ok=np.full(NP,False); unr=np.zeros(NP,bool)
    for p in range(NP):
        residual=np.max(np.abs(fd[cal[p],None]-cum[cal[p],:]),axis=0)
        adm=np.flatnonzero(np.abs(cum[p])>residual)
        if not len(adm): unr[p]=True; continue
        k=int(adm[0]); stop[p]=k+1; ok[p]=(np.sign(cum[p,k])==np.sign(fd[p]))
    return stop,ok,unr,fd
orders={s:make_order(site_w[s]) for s in sites}

# Full 5x5
rows=[]; pairrows=[]
for tgt in sites:
    ns,nok,nu,nfd=eval_order(site_w[tgt],orders[tgt]); nmean=np.nanmean(ns+1)
    for src in sites:
        s,ok,u,fd=eval_order(site_w[tgt],orders[src]); d=s-ns
        rows.append({'source_order':src,'target_site':tgt,'native_mean_total_cells':float(nmean),'mean_total_cells':float(np.nanmean(s+1)),'median_total_cells':float(np.nanmedian(s+1)),'excess_pct':float(100*(np.nanmean(s+1)/nmean-1)),'more_pairs':int(np.sum(d>0)),'same_pairs':int(np.sum(d==0)),'fewer_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'unresolved_pairs':int(u.sum()),'wrong_accepted_pairs':int((~ok & ~u).sum())})
        for p,(a,b) in enumerate(pairs):
            pairrows.append({'source_order':src,'target_site':tgt,'module_a':mods[a],'module_b':mods[b],'source_total_cells':s[p]+1 if np.isfinite(s[p]) else np.nan,'native_total_cells':ns[p]+1 if np.isfinite(ns[p]) else np.nan,'extra_cells':d[p] if np.isfinite(d[p]) else np.nan,'accepted_sign_correct':bool(ok[p]) if not u[p] else False,'unresolved':bool(u[p])})
full=pd.DataFrame(rows); full.to_csv(OUT/'transfer_5x5_full.csv',index=False); pd.DataFrame(pairrows).to_csv(OUT/'pairlevel_5x5_full.csv',index=False)

# Source portfolio excluding self
port=[]
for src in sites:
    q=full[(full.source_order==src)&(full.target_site!=src)]
    port.append({'source_order':src,'mean_offtarget_excess_pct':q.excess_pct.mean(),'median_pct':q.excess_pct.median(),'worst_pct':q.excess_pct.max(),'best_pct':q.excess_pct.min(),'wrong_accepted_total':q.wrong_accepted_pairs.sum(),'unresolved_total':q.unresolved_pairs.sum()})
port=pd.DataFrame(port).sort_values('mean_offtarget_excess_pct'); port.to_csv(OUT/'source_portfolio_5site.csv',index=False)

# Common five-site support
common5=set.intersection(*(site_sets[s] for s in sites)); common_w={}; support=[]
for site in ['Cocoa','Eugene','Golden']:
    ws=[]; in_n=com_n=0
    for (s,tech,mid),(q,sid) in recs.items():
        if s!=site: continue
        ws.append(bary_weights(q,common5)[0]); in_n+=len(q); com_n+=int(np.isin(sid,list(common5)).sum())
    common_w[site]=np.mean(np.vstack(ws),axis=0); support.append({'site':site,'inside_grid_n':in_n,'common5_n':com_n,'common5_pct':100*com_n/in_n})
for site,q,sid0 in [('Switzerland',q_sw,sid_sw),('Albuquerque',q_abq,sid_abq)]:
    common_w[site]=bary_weights(q,common5)[0]; support.append({'site':site,'inside_grid_n':len(q),'common5_n':int(np.isin(sid0,list(common5)).sum()),'common5_pct':100*np.isin(sid0,list(common5)).mean()})
corders={s:make_order(common_w[s]) for s in sites}
crows=[]
for tgt in sites:
    ns,_,_,_=eval_order(common_w[tgt],corders[tgt]); nmean=np.nanmean(ns+1)
    for src in sites:
        s,ok,u,_=eval_order(common_w[tgt],corders[src]); d=s-ns
        crows.append({'source_order':src,'target_site':tgt,'native_mean_total_cells':float(nmean),'mean_total_cells':float(np.nanmean(s+1)),'excess_pct':float(100*(np.nanmean(s+1)/nmean-1)),'more_pairs':int(np.sum(d>0)),'same_pairs':int(np.sum(d==0)),'fewer_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'unresolved_pairs':int(u.sum()),'wrong_accepted_pairs':int((~ok&~u).sum())})
common=pd.DataFrame(crows); common.to_csv(OUT/'transfer_5x5_common5.csv',index=False); pd.DataFrame(support).to_csv(OUT/'common5_support.csv',index=False)
cport=[]
for src in sites:
    q=common[(common.source_order==src)&(common.target_site!=src)]
    cport.append({'source_order':src,'common5_mean_offtarget_excess_pct':q.excess_pct.mean(),'common5_worst_pct':q.excess_pct.max(),'common5_best_pct':q.excess_pct.min(),'wrong_accepted_total':q.wrong_accepted_pairs.sum(),'unresolved_total':q.unresolved_pairs.sum()})
cport=pd.DataFrame(cport); cport.to_csv(OUT/'source_portfolio_common5.csv',index=False)

# Pooled5 and LOCO5
pool5=make_order(np.mean(np.vstack([site_w[s] for s in sites]),axis=0))
prows=[]
for tgt in sites:
    ns,_,_,_=eval_order(site_w[tgt],orders[tgt]); nmean=np.nanmean(ns+1)
    train=[s for s in sites if s!=tgt]; loco=make_order(np.mean(np.vstack([site_w[s] for s in train]),axis=0))
    for name,ordr in [('GlobalPooled5',pool5),('LOCO5',loco)]:
        s,ok,u,_=eval_order(site_w[tgt],ordr); d=s-ns
        prows.append({'sequence':name,'target_site':tgt,'native_mean_total_cells':float(nmean),'mean_total_cells':float(np.nanmean(s+1)),'excess_pct':float(100*(np.nanmean(s+1)/nmean-1)),'more_pairs':int(np.sum(d>0)),'same_pairs':int(np.sum(d==0)),'fewer_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'unresolved_pairs':int(u.sum()),'wrong_accepted_pairs':int((~ok&~u).sum())})
pooldf=pd.DataFrame(prows); pooldf.to_csv(OUT/'pooled_loco5.csv',index=False)

# Sign agreement matrix full endpoints
sigrows=[]
fds={s:eval_order(site_w[s],orders[s])[3] for s in sites}
for a,b in itertools.combinations(sites,2):
    same=(np.sign(fds[a])==np.sign(fds[b]))
    sigrows.append({'site_a':a,'site_b':b,'same_sign_pairs':int(same.sum()),'changed_pairs':int((~same).sum())})
pd.DataFrame(sigrows).to_csv(OUT/'sign_agreement_pairs.csv',index=False)

# Technology-stratified sensitivity on 15 core trajectories, all five source orders
techrows=[]
for (tgt,tech,mid),(q,sid0) in recs.items():
    tw=bary_weights(q)[0]; native_order=make_order(tw); ns,_,_,_=eval_order(tw,native_order); nmean=np.nanmean(ns+1)
    for src in sites:
        s,ok,u,_=eval_order(tw,orders[src]);
        techrows.append({'target_site':tgt,'technology':tech,'module_id':mid,'source_order':src,'native_mean_total_cells':float(nmean),'mean_total_cells':float(np.nanmean(s+1)),'excess_pct':float(100*(np.nanmean(s+1)/nmean-1)),'unresolved_pairs':int(u.sum()),'wrong_accepted_pairs':int((~ok&~u).sum())})
techdf=pd.DataFrame(techrows); techdf.to_csv(OUT/'technology_stratified_15x5.csv',index=False)
techsum=techdf.groupby('source_order').agg(n_targets=('excess_pct','size'),mean_excess_pct=('excess_pct','mean'),median_excess_pct=('excess_pct','median'),max_excess_pct=('excess_pct','max'),min_excess_pct=('excess_pct','min'),wrong_accepted_total=('wrong_accepted_pairs','sum'),unresolved_total=('unresolved_pairs','sum')).reset_index(); techsum.to_csv(OUT/'technology_stratified_summary.csv',index=False)

# Random-order 1000 reference per off-target pair, source-positive node set fixed. Seed locked.
rng=np.random.default_rng(20260829); randrows=[]; N=1000
for tgt in sites:
    ns,_,_,_=eval_order(site_w[tgt],orders[tgt]); native_mean=np.nanmean(ns+1)
    for src in sites:
        if src==tgt: continue
        elig=orders[src].copy(); vals=[]
        for _ in range(N):
            s,ok,u,_=eval_order(site_w[tgt],rng.permutation(elig)); vals.append(np.nanmean(s+1))
        vals=np.asarray(vals); det=float(full.query('source_order==@src and target_site==@tgt').mean_total_cells.iloc[0])
        randrows.append({'source_order':src,'target_site':tgt,'N_random':N,'deterministic_mean_cells':det,'native_mean_cells':float(native_mean),'random_median_mean_cells':float(np.median(vals)),'random_p2_5':float(np.quantile(vals,.025)),'random_p97_5':float(np.quantile(vals,.975)),'deterministic_lower_is_better_percentile':float(100*np.mean(vals<=det))})
pd.DataFrame(randrows).to_csv(OUT/'random_order_reference_1000_5site.csv',index=False)

# Symmetric distances over node weights. JS/Hellinger/TV and exact discrete 2D Wasserstein LP over node coords normalized to grid ranges.
def jsdist(p,q):
    p=np.asarray(p); q=np.asarray(q); m=.5*(p+q); eps=1e-300
    klpm=np.sum(np.where(p>0,p*np.log((p+eps)/(m+eps)),0)); klqm=np.sum(np.where(q>0,q*np.log((q+eps)/(m+eps)),0)); return math.sqrt(.5*(klpm+klqm))
def hell(p,q): return float(np.linalg.norm(np.sqrt(p)-np.sqrt(q))/math.sqrt(2))
def tv(p,q): return float(.5*np.abs(p-q).sum())
xy_norm=np.column_stack([(xy[:,0]-xy[:,0].min())/(np.ptp(xy[:,0])),(xy[:,1]-xy[:,1].min())/(np.ptp(xy[:,1]))])
C=np.linalg.norm(xy_norm[:,None,:]-xy_norm[None,:,:],axis=2); n=len(xy)
Aeq=[]; beq=[]
# We'll build for each p,q to avoid one redundant constraint issue using n row + n-1 col constraints
for i in range(n):
    row=np.zeros(n*n); row[i*n:(i+1)*n]=1; Aeq.append(row)
for j in range(n-1):
    row=np.zeros(n*n); row[j::n]=1; Aeq.append(row)
Aeq=np.asarray(Aeq)
def w1(p,q):
    b=np.r_[p,q[:-1]]; res=linprog(C.ravel(),A_eq=Aeq,b_eq=b,bounds=(0,None),method='highs');
    if not res.success: raise RuntimeError(res.message)
    return float(res.fun)
drows=[]
for a,b in itertools.combinations(sites,2):
    p=site_w[a]; q=site_w[b]
    ab=float(full.query('source_order==@a and target_site==@b').excess_pct.iloc[0]); ba=float(full.query('source_order==@b and target_site==@a').excess_pct.iloc[0])
    drows.append({'site_a':a,'site_b':b,'jensen_shannon_distance':jsdist(p,q),'hellinger_distance':hell(p,q),'total_variation_distance':tv(p,q),'wasserstein1_normalized_GT':w1(p,q),'a_to_b_excess_pct':ab,'b_to_a_excess_pct':ba,'mean_bidirectional_excess_pct':.5*(ab+ba),'max_directional_excess_pct':max(ab,ba),'directional_abs_gap_pct':abs(ab-ba)})
dist=pd.DataFrame(drows); dist.to_csv(OUT/'environment_distance_5site.csv',index=False)
corr=[]
for dm in ['jensen_shannon_distance','hellinger_distance','total_variation_distance','wasserstein1_normalized_GT']:
    for om in ['mean_bidirectional_excess_pct','max_directional_excess_pct','directional_abs_gap_pct']:
        sp=spearmanr(dist[dm],dist[om]); pr=pearsonr(dist[dm],dist[om])
        corr.append({'distance_metric':dm,'outcome':om,'n_pairs':len(dist),'spearman_rho':float(sp.statistic),'spearman_p_nominal':float(sp.pvalue),'pearson_r':float(pr.statistic),'pearson_p_nominal':float(pr.pvalue)})
pd.DataFrame(corr).to_csv(OUT/'environment_distance_correlations.csv',index=False)

# Summary json
summary={
 'switzerland_source_files':[{'file':a,'sha256':b,'rows':c} for a,b,c in src_hash],
 'switzerland_total_rows':int(len(sw)),'switzerland_valid_rows':int(valid.sum()),'switzerland_inside_grid_rows':int(len(q_sw)),'switzerland_inside_grid_pct':float(100*len(q_sw)/valid.sum()),
 'albuquerque_valid_5min_rows':int(v.sum()),'albuquerque_inside_grid_rows':int(len(q_abq)),'albuquerque_inside_grid_pct':float(100*len(q_abq)/v.sum()),
 'common5_simplices_n':int(len(common5)),'full_source_portfolio':port.to_dict(orient='records'),'common5_source_portfolio':cport.to_dict(orient='records'),
 'key_reversal_tests':{k:float(full.query('source_order==@src and target_site==\'Switzerland\'').excess_pct.iloc[0]) for k,src in [('Albuquerque_to_Switzerland','Albuquerque'),('Golden_to_Switzerland','Golden'),('Cocoa_to_Switzerland','Cocoa'),('Eugene_to_Switzerland','Eugene')]},
 'switzerland_as_source':{t:float(full.query("source_order=='Switzerland' and target_site==@t").excess_pct.iloc[0]) for t in sites if t!='Switzerland'},
 'pooled5':pooldf.to_dict(orient='records'), 'sign_agreement':pd.DataFrame(sigrows).to_dict(orient='records'), 'technology_summary':techsum.to_dict(orient='records')
}
(OUT/'summary_5site.json').write_text(json.dumps(summary,indent=2)+'\n')
print('FULL 5x5')
print(full.to_string(index=False))
print('\nPORTFOLIO')
print(port.to_string(index=False))
print('\nCOMMON5 PORT')
print(cport.to_string(index=False))
print('\nPOOLED')
print(pooldf.to_string(index=False))
print('\nKEY REVERSAL',summary['key_reversal_tests'])
