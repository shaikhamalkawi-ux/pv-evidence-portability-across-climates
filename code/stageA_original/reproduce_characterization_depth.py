from pathlib import Path
import itertools,re,json,math
import numpy as np,pandas as pd
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
MAT=ROOT/'data/sandia_iec61853_performance_matrix_long.csv'
SLIM=ROOT/'mpert_core'
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
# Load IEC panel
mat=pd.read_csv(MAT); mods=sorted(mat.module_id.unique())
coords=mat[['irradiance_Wm2','temperature_C']].drop_duplicates().sort_values(['irradiance_Wm2','temperature_C']).reset_index(drop=True)
xy=coords[['irradiance_Wm2','temperature_C']].to_numpy(float); tri=Delaunay(xy)
Z=np.empty((len(mods),len(xy)))
for ii,m in enumerate(mods):
    mm=coords.merge(mat[mat.module_id==m],on=['irradiance_Wm2','temperature_C'],how='left')
    pstc=float(mm.loc[(mm.irradiance_Wm2==1000)&(mm.temperature_C==25),'Pmp_W'].iloc[0]); Z[ii]=mm.Pmp_W.to_numpy(float)/pstc
stc=int(coords.index[(coords.irradiance_Wm2==1000)&(coords.temperature_C==25)][0])
# exact barycentric node weights for q; optional simplex filter
def bary_weights(q, simplex_keep=None):
    q=np.asarray(q,float); sid=tri.find_simplex(q); inside=sid>=0
    if simplex_keep is not None:
        inside &= np.isin(sid,list(simplex_keep))
    qq=q[inside]; ss=sid[inside]
    T=tri.transform[ss,:2,:]; r=qq-tri.transform[ss,2,:]
    b12=np.einsum('nij,nj->ni',T,r); bary=np.c_[b12,1-b12.sum(axis=1)]
    verts=tri.simplices[ss]
    w=np.zeros(len(xy),float)
    for k in range(3): w += np.bincount(verts[:,k],weights=bary[:,k],minlength=len(xy))
    w/=len(qq)
    return w, inside, sid
# Read slim core
recs={}; site_simplexes={s:[] for s in ['Cocoa','Eugene','Golden']}
for fp in sorted(SLIM.glob('*.csv')):
    m=re.match(r'(Cocoa|Eugene|Golden)_(.+?)(\d+)\.csv',fp.name); site,tech,mid=m.groups()
    df=pd.read_csv(fp,usecols=['poa','tmod','pmp'])
    for c in ['poa','tmod','pmp']:
        df[c]=pd.to_numeric(df[c],errors='coerce'); df.loc[df[c]<=-9000,c]=np.nan
    valid=df.poa.notna()&df.tmod.notna()&df.pmp.notna()&(df.poa>0)&(df.pmp>=0)
    q=df.loc[valid,['poa','tmod']].to_numpy(float)
    sid=tri.find_simplex(q); q=q[sid>=0]; sid=sid[sid>=0]
    recs[(site,tech,mid)]=(q,sid); site_simplexes[site].append(sid)
site_sets={s:set(np.unique(np.concatenate(v)).tolist()) for s,v in site_simplexes.items()}
common_simplexes=set.intersection(*(site_sets[s] for s in ['Cocoa','Eugene','Golden']))
# full and common weights: equal average across five technologies per site
site_w={}; common_w={}; common_support_rows=[]
for site in ['Cocoa','Eugene','Golden']:
    ws=[]; wc=[]
    for (s,tech,mid),(q,sid) in recs.items():
        if s!=site: continue
        w,_,_=bary_weights(q); cwmask=np.isin(sid,list(common_simplexes)); w2,_,_=bary_weights(q,common_simplexes)
        ws.append(w); wc.append(w2)
        common_support_rows.append({'site':site,'technology':tech,'module_id':mid,'inside_grid_n':len(q),'shared_simplex_n':int(cwmask.sum()),'shared_simplex_pct':100*cwmask.mean()})
    site_w[site]=np.mean(np.vstack(ws),axis=0); common_w[site]=np.mean(np.vstack(wc),axis=0)
pd.DataFrame(common_support_rows).to_csv(OUT/'common_simplex_support.csv',index=False)
# R&S structures
pairs=list(itertools.combinations(range(len(mods)),2)); pair_index={p:i for i,p in enumerate(pairs)}; NP=len(pairs)
def pair_struct(w):
    full=Z@w; contrib=np.vstack([w*(Z[a]-Z[b]) for a,b in pairs]); fd=contrib.sum(axis=1); cal=[]
    for a,b in pairs:
        retained=[i for i in range(len(mods)) if i not in {a,b}]
        cal.append(np.array([pair_index[(x,y)] for x,y in itertools.combinations(retained,2)],int))
    return full,contrib,fd,cal
def make_order(w):
    elig=[j for j in range(len(xy)) if j!=stc and w[j]>1e-14]
    return np.array(sorted(elig,key=lambda j:(-w[j],xy[j,0],xy[j,1])),int)
def eval_order(w,order):
    full,contrib,fd,cal=pair_struct(w); cum=np.cumsum(contrib[:,order],axis=1)
    stop=np.full(NP,np.nan); ok=np.full(NP,False); unresolved=np.zeros(NP,bool)
    for p in range(NP):
        residual=np.max(np.abs(fd[cal[p],None]-cum[cal[p],:]),axis=0)
        adm=np.flatnonzero(np.abs(cum[p])>residual)
        if not len(adm): unresolved[p]=True; continue
        k=int(adm[0]); stop[p]=k+1; ok[p]=(np.sign(cum[p,k])==np.sign(fd[p]))
    return stop,ok,unresolved,fd,full
orders={s:make_order(w) for s,w in site_w.items()}; common_orders={s:make_order(w) for s,w in common_w.items()}
# pair-level full transfer
pairrows=[]; transfer=[]
for tgt,w in site_w.items():
    native_stop,_,_,_,_=eval_order(w,orders[tgt])
    for src,order in orders.items():
        s,ok,unres,_,_=eval_order(w,order)
        for p,(a,b) in enumerate(pairs):
            pairrows.append({'source_order':src,'target_climate':tgt,'module_a':mods[a],'module_b':mods[b],'total_cells':s[p]+1 if np.isfinite(s[p]) else np.nan,'target_native_total_cells':native_stop[p]+1,'extra_cells_vs_target_native':(s[p]-native_stop[p]) if np.isfinite(s[p]) else np.nan,'accepted_sign_correct':bool(ok[p]) if not unres[p] else False,'unresolved':bool(unres[p])})
        d=s-native_stop
        transfer.append({'source_order':src,'target_climate':tgt,'mean_total_cells':float(np.nanmean(s+1)),'median_total_cells':float(np.nanmedian(s+1)),'unresolved_pairs':int(unres.sum()),'wrong_accepted_pairs':int((~ok & ~unres).sum()),'worse_pairs':int(np.sum(d>0)),'tie_pairs':int(np.sum(d==0)),'better_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'mean_extra_cells':float(np.nanmean(d)),'max_extra_cells':float(np.nanmax(d)),'min_extra_cells':float(np.nanmin(d))})
pairdf=pd.DataFrame(pairrows); pairdf.to_csv(OUT/'pair_level_transport_burden.csv',index=False)
transfer=pd.DataFrame(transfer); transfer.to_csv(OUT/'pair_level_transport_summary.csv',index=False)
# common support transfer: both weighting and order restricted to shared observed IEC simplexes
ctr=[]
for tgt,w in common_w.items():
    native_stop,_,_,_,_=eval_order(w,common_orders[tgt])
    for src,order in common_orders.items():
        s,ok,unres,_,_=eval_order(w,order); d=s-native_stop
        ctr.append({'source_order':src,'target_climate':tgt,'mean_total_cells':float(np.nanmean(s+1)),'native_mean_total_cells':float(np.nanmean(native_stop+1)),'penalty_pct':100*(np.nanmean(s+1)/np.nanmean(native_stop+1)-1),'worse_pairs':int(np.sum(d>0)),'tie_pairs':int(np.sum(d==0)),'better_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'unresolved_pairs':int(unres.sum()),'wrong_accepted_pairs':int((~ok & ~unres).sum())})
common_transfer=pd.DataFrame(ctr); common_transfer.to_csv(OUT/'common_support_transfer.csv',index=False)
# LOCO and global pooled sequences. Order uses no target-climate weights; evaluation remains target-climate conditional.
lo=[]; lo_orders={}
for tgt in ['Cocoa','Eugene','Golden']:
    train=[s for s in ['Cocoa','Eugene','Golden'] if s!=tgt]; wtrain=np.mean(np.vstack([site_w[s] for s in train]),axis=0); lo_orders[tgt]=make_order(wtrain)
global_order=make_order(np.mean(np.vstack([site_w[s] for s in ['Cocoa','Eugene','Golden']]),axis=0))
for tgt,w in site_w.items():
    ns,_,_,_,_=eval_order(w,orders[tgt]); loco,ok,unres,_,_=eval_order(w,lo_orders[tgt]); glob,gok,gun,_,_=eval_order(w,global_order)
    for name,s,o,u in [('LOCO',loco,ok,unres),('GlobalPooled',glob,gok,gun)]:
        d=s-ns
        lo.append({'target_climate':tgt,'sequence':name,'mean_total_cells':float(np.nanmean(s+1)),'target_native_mean_total_cells':float(np.nanmean(ns+1)),'excess_pct':100*(np.nanmean(s+1)/np.nanmean(ns+1)-1),'worse_pairs':int(np.sum(d>0)),'tie_pairs':int(np.sum(d==0)),'better_pairs':int(np.sum(d<0)),'median_extra_cells':float(np.nanmedian(d)),'unresolved_pairs':int(u.sum()),'wrong_accepted_pairs':int((~o & ~u).sum())})
loco=pd.DataFrame(lo); loco.to_csv(OUT/'loco_global_sequence_transfer.csv',index=False)
# Random-order scale reference over the same target-positive node set.
# N=1000 is frozen for this strengthened release; it is not used to tune any sequence.
rng=np.random.default_rng(20260813); rr=[]; N=1000
for tgt,w in site_w.items():
    elig=make_order(w).copy(); vals=[]
    for r in range(N):
        s,ok,u,_,_=eval_order(w,rng.permutation(elig)); vals.append(np.nanmean(s+1))
    vals=np.asarray(vals); native=np.nanmean(eval_order(w,orders[tgt])[0]+1); loco_mean=float(loco.query("target_climate==@tgt and sequence=='LOCO'").mean_total_cells.iloc[0]); glob_mean=float(loco.query("target_climate==@tgt and sequence=='GlobalPooled'").mean_total_cells.iloc[0])
    rr.append({'target_climate':tgt,'N_random':N,'random_median_mean_cells':float(np.median(vals)),'random_p2_5':float(np.quantile(vals,.025)),'random_p97_5':float(np.quantile(vals,.975)),'target_native_mean_cells':float(native),'random_le_native_n':int(np.sum(vals<=native)),'native_percentile':float(100*np.mean(vals<=native)),'LOCO_mean_cells':loco_mean,'LOCO_percentile_vs_random':float(100*np.mean(vals<=loco_mean)),'global_mean_cells':glob_mean,'global_percentile_vs_random':float(100*np.mean(vals<=glob_mean))})
pd.DataFrame([{k:v for k,v in r.items() if k in ['target_climate','N_random','random_median_mean_cells','random_p2_5','random_p97_5','target_native_mean_cells','random_le_native_n','native_percentile']} for r in rr]).to_csv(OUT/'random_order_reference_1000.csv',index=False)
# useful order similarity via Kendall rank on union (diagnostic only)
from scipy.stats import kendalltau
sim=[]
for a,b in itertools.combinations(['Cocoa','Eugene','Golden'],2):
    allnodes=[j for j in range(len(xy)) if j!=stc]
    ra={j:(list(orders[a]).index(j)+1 if j in set(orders[a]) else 999) for j in allnodes}; rb={j:(list(orders[b]).index(j)+1 if j in set(orders[b]) else 999) for j in allnodes}
    tau=kendalltau([ra[j] for j in allnodes],[rb[j] for j in allnodes]).statistic
    sim.append({'climate_a':a,'climate_b':b,'kendall_tau_order':float(tau)})
pd.DataFrame(sim).to_csv(OUT/'order_similarity_diagnostic.csv',index=False)
# summary
cs=pd.DataFrame(common_support_rows).groupby('site',as_index=False)[['shared_simplex_n','inside_grid_n']].sum(); common_pct={r.site:100*r.shared_simplex_n/r.inside_grid_n for r in cs.itertuples()}; summary={'common_simplexes_n':len(common_simplexes),'grid_simplices_total':len(tri.simplices),'common_support_pct_by_site':common_pct,'pair_transfer':transfer.to_dict(orient='records'),'common_transfer':common_transfer.to_dict(orient='records'),'loco':loco.to_dict(orient='records'),'random':rr}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
# figures
# All six off-diagonal source-to-target transfers.
fig,ax=plt.subplots(figsize=(8.7,4.7))
keys=[('Cocoa','Eugene'),('Cocoa','Golden'),('Eugene','Cocoa'),('Eugene','Golden'),('Golden','Cocoa'),('Golden','Eugene')]
data=[]; labs=[]
for src,tgt in keys:
    v=pairdf.query('source_order==@src and target_climate==@tgt').extra_cells_vs_target_native.to_numpy()
    data.append(v); labs.append(f'{src}â{tgt}')
ax.boxplot(data,tick_labels=labs,showmeans=True)
ax.axhline(0,ls='--',lw=1)
ax.set_ylabel('Extra IEC cells vs target-conditioned heuristic')
ax.set_xlabel('Transported measurement order')
ax.tick_params(axis='x',rotation=25)
fig.tight_layout(); fig.savefig(OUT/'pair_level_excess_burden.png',dpi=240); plt.close(fig)
# LOCO and all-climate pooled excess burden relative to target-conditioned heuristic.
fig,ax=plt.subplots(figsize=(7.6,4.5))
tgts=['Cocoa','Eugene','Golden']; x=np.arange(len(tgts)); width=.36
lo_vals=[float(loco.query("target_climate==@t and sequence=='LOCO'").excess_pct.iloc[0]) for t in tgts]
gl_vals=[float(loco.query("target_climate==@t and sequence=='GlobalPooled'").excess_pct.iloc[0]) for t in tgts]
ax.bar(x-width/2,lo_vals,width,label='LOCO: other two climates')
ax.bar(x+width/2,gl_vals,width,label='Global pooled: all three')
ax.axhline(0,ls='--',lw=1)
ax.set_xticks(x,tgts); ax.set_ylabel('Excess mean burden vs target-conditioned heuristic (%)')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT/'pooled_sequence_excess_burden.png',dpi=240); plt.close(fig)
print(json.dumps(summary,indent=2))
