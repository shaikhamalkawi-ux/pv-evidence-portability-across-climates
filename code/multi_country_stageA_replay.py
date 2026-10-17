#!/usr/bin/env python3
"""Flagship A R3 external fixed-rule Stage A replay -- Germany/Italy/Brazil.

Scientific freeze: PROJECT_66_PREOUTCOME_PROTOCOL_REGISTER

CRITICAL: no optimization/retraining/stopping-rule editing; imports exact frozen
original R3 pre-Full-5x5 scientific implementation from verified source archive.
External data represent field *operating-state distributions*, never performance
observations of the nine original R3 response-panel products.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, sys, zipfile
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

BASELINE_SCRIPT_SHA='79ec83a814a0f665c310d75de42c40471e9491f4ca09f1d54f1ad26b5b8eddc9'
SOURCE_HASHES={
 'PV_temperature_model_data_2018_System_1_1min.dat.bin':'0c053f00a3e5b6243e4995ee034757fa606eebd8cccef849cfddb11d4c1138bf',
 'PV_temperature_model_data_2018_System_2A_1min.dat.bin':'62ef9b287e4a223bc33bea944e1f3c84a8fa7788d5a4a9d78c7ecaf3edc022fc',
 'PV_temperature_model_data_2019_System_2B_1min.dat.bin':'6baedb896ec5e8ca9c975f2c7bacc2da86f82581d5347f93c82ccbbaa37cb1f1',
 'BR-PVGen_meteorological.zip':'a4b23123c16bf6a97a8d282e6ad18c2e697ac990d0b96602c68c6b2abfce240f',
 'BR-PVGen_metadata.csv':'ba45f4dfb557bbfca37c3ee16c8b7d2a5f0aec9fad4e6b6774be760c4852237c',
 'PV_Q2.csv':'0813f386440355fc0e24a3f8825e66d678811c5ad24af5a393738564c50ceaeb',
}

def sha(path,block=1<<21):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(block),b''):h.update(b)
    return h.hexdigest()

def export_csv(path,rows):
    if not rows:return
    df=pd.DataFrame(rows)
    df.to_csv(path,index=False,float_format='%.14g')
    print('WRITTEN',path,len(df))

def assert_reference_parity(ns,ref,tol=1e-8):
    w=ns['site_w'];o=ns['orders'];ev=ns['eval_order']
    q=pd.read_csv(ref);n=0;errs=[];status=[]
    for row in q.to_dict('records'):
        sw=w[row['target_site']];base=ev(sw,o[row['target_site']]);other=ev(sw,o[row['source_order']]);
        local=float(np.nanmean(base[0]+1));current=float(np.nanmean(other[0]+1));pct=100*(current/local-1)
        errs.append(abs(pct-float(row['excess_pct'])))
        status.append([int(np.sum(~other[1] & ~other[2])),int(other[2].sum()),row['wrong_accepted_pairs'],row['unresolved_pairs']]);n+=1
    assert n==25 and max(errs)<=tol,('original 25-cell reference parity FAILED',n,max(errs))
    assert all(int(s[0])==int(s[2]) and int(s[1])==int(s[3]) for s in status),'baseline wrong/unresolved changed'
    return {'original_R3_25_of_25_cells_PASS':True,'original_R3_max_abs_pct_point_diff':float(max(errs)),'original_R3_stop_error_flags_match':True}

class Runner:
    def __init__(self,ns,out):
        self.ns=ns;self.out=out;self.summary=[];self.pairs=[];self.temporal=[];self.source_gate=[];self.sites=[];self.weights={};self.admitted=0
        self.ev=ns['eval_order'];self.mk=ns['make_order'];self.bw=ns['bary_weights'];self.tri=ns['tri'];self.old=ns['orders'];self.names=ns['sites'];self.pidx=ns['pairs'];self.mods=ns['mods'];self.common=set.intersection(*(ns['site_sets'][site] for site in ns['sites']))
    def process(self,identifier,source,region,method,q,times,raw_n,metadata=None,sensitivity=False,min_n=1000,min_days=30):
        q=np.asarray(q,float)
        t=pd.Series(times).reset_index(drop=True)
        good=np.all(np.isfinite(q),axis=1)&(q[:,0]>0)
        g=q[good];tt=t.loc[good].reset_index(drop=True)
        sid=self.tri.find_simplex(g) if len(g) else np.array([],int)
        valid=sid>=0;in_q=g[valid];in_t=tt.loc[valid].reset_index(drop=True)
        days=int(in_t.dt.normalize().nunique()) if len(in_t) else 0
        check={'target_id':identifier,'source_dataset':source,'region':region,'time_series_type':method,'n_raw_rows':int(raw_n),'n_input_rows':int(len(q)),'n_valid_daylight_paired':int(len(g)),'n_in_R3_grid':int(len(in_q)),'pct_in_R3_grid_conditional_paired':float(100*valid.mean()) if len(valid) else None,'n_unique_in_grid_dates':days,'date_first_in_grid':str(in_t.min()) if len(in_t) else None,'date_last_in_grid':str(in_t.max()) if len(in_t) else None,'pct_common_old5_simplices':float(100*np.isin(sid[valid],list(self.common)).mean()) if len(in_q) and self.common else None,'admission_threshold_rows':min_n,'admission_threshold_days':min_days,'is_repeated_sensitivity':sensitivity,'sensor_protocol_status':'OBSERVED_MEASURED_GPOA_AND_MODULE_T; IN-SOURCE RESAMPLING/AGGREGATION DISCLOSED',**(metadata or {})}
        allowed=len(in_q)>=min_n and days>=min_days
        check['numeric_external_gate']='PASS' if allowed else 'HOLD_INSUFFICIENT_SUPPORT';self.source_gate.append(check)
        if not allowed: return
        w=self.bw(in_q)[0]
        assert np.all(np.isfinite(w)) and np.isclose(w.sum(),1,rtol=0,atol=2e-12)
        native_order=self.mk(w);ns,okn,unr,full=self.ev(w,native_order)
        ref=float(np.nanmean(ns+1));unr_n=unr.copy()
        # Predeclared near-tie diagnostic is dimensionless and not metrological.
        absfd=np.abs(full);ties100=int(np.sum(absfd<=1e-4));ties1000=int(np.sum(absfd<=1e-3));
        if np.sum(np.isfinite(ns))==0:raise ValueError('all target local pairs unresolved: '+identifier)
        for source_order in ['Target-local heuristic',*self.names]:
            order=native_order if source_order=='Target-local heuristic' else self.old[source_order]
            stops,ok,unr,fd=self.ev(w,order)
            assert np.max(abs(fd-full))<1e-12
            wrong=~ok & ~unr
            n_res=int(np.sum(~unr))
            if np.any(unr) or np.any(unr_n):
                safe_excess=None   # ban comparing incomplete horizons with complete local heuristic
            else:
                safe_excess=float(100*(np.mean(stops+1)/ref-1))
            row={'target_id':identifier,'source_dataset':source,'region':region,'source_order':source_order,'time_series_type':method,'is_repeated_sensitivity':sensitivity,'n_in_R3_grid':int(len(in_q)),'n_in_grid_days':days,'n_held_pairs':int(len(stops)),'n_resolved':n_res,'n_unresolved':int(unr.sum()),'n_wrong_accepted':int(wrong.sum()),'n_wrong_near_tie_le1e4':int(np.sum(wrong&(absfd<=1e-4))),'n_wrong_near_tie_le1e3':int(np.sum(wrong&(absfd<=1e-3))),'n_full_margin_le1e4':ties100,'n_full_margin_le1e3':ties1000,'target_local_mean_cells_resolved':ref,'source_mean_cells_resolved':float(np.nanmean(stops+1)) if n_res else None,'directional_excess_pct_all_resolved_only':safe_excess,'mean_cells_if_any_unresolved_resolved_only_NOT_comparable':float(np.nanmean(stops+1)) if np.any(unr) and n_res else None,'min_nonzero_full_abs_pair_delta':float(np.min(absfd[absfd>0]))}
            self.summary.append(row)
            for p,(a,b) in enumerate(self.pidx):
                self.pairs.append({'target_id':identifier,'source_order':source_order,'module_a':self.mods[a],'module_b':self.mods[b],'stop_cells':float(stops[p]+1) if np.isfinite(stops[p]) else None,'target_local_stop_cells':float(ns[p]+1) if np.isfinite(ns[p]) else None,'accepted_sign_correct':bool(ok[p]),'unresolved':bool(unr[p]),'wrong_accepted':bool(wrong[p]),'full_target_normalized_difference':float(fd[p]),'near_tie_1e4':bool(absfd[p]<=1e-4)})
        self.weights[identifier]=w;self.sites.append(identifier)
        print('EXTERNAL',identifier,'grid',len(in_q),'days',days,'native',round(ref,4),'best historical',sorted([(r['directional_excess_pct_all_resolved_only'] if r['directional_excess_pct_all_resolved_only'] is not None else np.inf,r['source_order']) for r in self.summary[-6:] if r['source_order']!='Target-local heuristic'])[0])


def main():
    a=argparse.ArgumentParser();a.add_argument('--input-root',default='/mnt/data');a.add_argument('--baseline-dir',default='/mnt/data/safi_r3_work/r3_src/Stage_A_Characterization_Order');a.add_argument('--swiss-dir',default='/mnt/data/safi_r3_work/sw12');a.add_argument('--albuquerque-file',default='/mnt/data/tmod_sample_data.nc.cdf');a.add_argument('--out-dir',default='/mnt/data/project62_multicountry_r3ext/results');args=a.parse_args();inp=Path(args.input_root);bd=Path(args.baseline_dir);out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    code=bd/'directional_transfer_5site.py'
    assert sha(code)==BASELINE_SCRIPT_SHA,'ORIGINAL SOURCE SCRIPT SHA MISMATCH'
    hashes={}
    for f,h in SOURCE_HASHES.items():
        fn=inp/f;current=sha(fn)
        assert current==h,(f,'SOURCE SHA MISMATCH',current)
        hashes[f]={'sha256':current,'original_bytes':fn.stat().st_size,'checksum_verified':True}
    codebase=code.read_text(encoding='utf8');prefix=codebase.split('# Full 5x5')[0];assert len(prefix)>6000 and 'orders={s:make_order(site_w[s]) for s in sites}' in prefix
    argv=sys.argv.copy();sys.argv=[str(code),'--task13-dir',str(args.swiss_dir),'--albuquerque-nc',str(args.albuquerque_file),'--output-dir',str(out/'r3_original_prefix_output')]
    ns={'__file__':str(code),'__name__':'external_r3_unmodified_prefix'}
    exec(compile(prefix,str(code),'exec'),ns);sys.argv=argv
    parity=assert_reference_parity(ns,bd/'outputs/r12_directional/transfer_5x5_full.csv')
    print('BASELINE 25/25 PASS',json.dumps(parity))
    x=Runner(ns,out)
    # Germany: 3 seasonal/system trajectories, each one-minute publisher-resampled.
    for f in ['PV_temperature_model_data_2018_System_1_1min.dat.bin','PV_temperature_model_data_2018_System_2A_1min.dat.bin','PV_temperature_model_data_2019_System_2B_1min.dat.bin']:
        df=pd.read_csv(inp/f,comment='#',sep=';',low_memory=False)
        q=df[['Gtotpoa_Wm2','T_module_C']].apply(pd.to_numeric,errors='coerce').to_numpy(float)
        times=pd.to_datetime(df['Timestamp_UTC'],utc=True,errors='coerce')
        assert not times.isna().any() and not times.duplicated().any()
        x.process(f.replace('PV_temperature_model_data_','').replace('_1min.dat.bin',''),'D22_Germany','Allgau Germany','1min resampled field data',q,times,len(df),metadata={'field_file':f,'instrument_T':'T_module_C','instrument_G':'Gtotpoa_Wm2','timestamp_semantics':'UTC','source_site_identity':f.split('_System_')[1].split('_1min')[0]},min_n=1000,min_days=30)
    # Italy primary first of 3 module-back temperature channels; secondary sensor sensitivity.
    df=pd.read_csv(inp/'PV_Q2.csv',low_memory=False)
    g=pd.to_numeric(df['irradiance'],errors='coerce').to_numpy(float)
    t=pd.to_datetime(df['date'].astype('string')+' '+df['time'].astype('string'),format='%Y%m%d %H:%M:%S',errors='coerce');assert t.notna().all() and not t.duplicated().any()
    for i,ch in enumerate(['inv1_tpan','inv2_tpan','inv3_tpan']):
        temp=pd.to_numeric(df[ch],errors='coerce').to_numpy(float)
        q=np.column_stack([g,temp])
        x.process('D24_Trieste_'+ch,'D24_Italy','Trieste Italy','15min site-averaged module sensor, timezone NAIVE',q,t,len(df),metadata={'instrument_T':ch,'instrument_G':'irradiance','field_site_identity':'ONE_Q2_BUILDING_15.9kW_2013_2021','source_site_identity':'Q2','source_module_identity':'53 SunPower SPR300-WHT modules','timestamp_semantics':'LOCAL SOURCE DATETIME; timezone not reported'},sensitivity=i>0,min_n=1000,min_days=30)
        if i==0:
            # Annual-split sensitivity from native inv1 module sensor only; no cross-year pooling/claims.
            for year in sorted(t.dt.year.dropna().unique()):
                sel=(t.dt.year==year).to_numpy(bool)
                x.process(f'D24_Trieste_inv1_Y{year}','D24_Italy_annual','Trieste Italy','annual slice of same 15min site, NOT independent climate',q[sel],t.loc[sel].reset_index(drop=True),int(sel.sum()),metadata={'instrument_T':ch,'instrument_G':'irradiance','field_site_identity':'ONE_Q2_BUILDING','source_site_identity':'Q2','source_year':int(year),'timestamp_semantics':'LOCAL SOURCE DATETIME; timezone not reported'},sensitivity=True,min_n=1000,min_days=30)
    # Brazil each plant is one separate WMA-treated station, never interpret 51 files as 51 admitted sites.
    meta=pd.read_csv(inp/'BR-PVGen_metadata.csv').set_index('id')
    with zipfile.ZipFile(inp/'BR-PVGen_meteorological.zip') as z:
        assert z.testzip() is None
        files=sorted(f for f in z.namelist() if f.endswith('.csv'));assert len(files)==51
        for i,fn in enumerate(files):
            df=pd.read_csv(z.open(fn),low_memory=False)
            ident=Path(fn).stem
            assert df['ps_id'].dropna().astype(str).nunique()<=1
            assert ident in meta.index
            g=pd.to_numeric(df['poa_irradiance_wm2'],errors='coerce').to_numpy(float)
            temp=pd.to_numeric(df['panel_temperature_celsius'],errors='coerce').to_numpy(float)
            cp=pd.to_numeric(df['document_count_poa_irradiance_wm2'],errors='coerce').to_numpy(float)
            ct=pd.to_numeric(df['document_count_panel_temperature_celsius'],errors='coerce').to_numpy(float)
            ip=~df['interpolated_keys_poa_irradiance_wm2'].astype('string').str.strip().str.lower().eq('true').fillna(False).to_numpy(bool)
            it=(~df['interpolated_keys_panel_temperature_celsius'].astype('string').str.strip().str.lower().eq('true').fillna(False).to_numpy(bool) if 'interpolated_keys_panel_temperature_celsius' in df.columns else np.zeros(len(df),dtype=bool))
            good=(cp>0)&(ct>0)&ip&it
            # Drop ineligible flagged or count-zero pairs before calculating target G/T geometry.
            gg=np.where(good,g,np.nan);tt=np.where(good,temp,np.nan)
            q=np.column_stack([gg,tt]);times=pd.to_datetime(df['datetime'],utc=True,errors='coerce')
            assert times.notna().all() and not times.duplicated().any()
            info=meta.loc[ident]
            x.process('D09_'+ident,'D09_Brazil','Brazil/'+str(info['brazil_federative_unit']),'15min WMA publisher-aggregated; non-explicitly-flagged and raw count positive',q,times,len(df),metadata={'field_file':fn,'source_site_identity':ident,'brazil_federative_unit':str(info['brazil_federative_unit']),'structure_type':str(info['structure_type']),'nominal_power_mw':float(info['nominal_power_mw']),'source_panel_bifacial':str(info['is_panel_bifacial']),'source_records_processed_WMA':True,'n_poa_interpolation_explicit_TRUE':int((~ip).sum()),'n_tmod_interpolation_explicit_TRUE':int((~it).sum()),'n_raw_document_count_positive_both':int(np.sum((cp>0)&(ct>0))),'has_temperature_interpolation_flag_column':bool('interpolated_keys_panel_temperature_celsius' in df.columns)},min_n=1000,min_days=30)
            # Quarter-by-quarter sensitivity under SAME frozen source orders.
            # The primary per-plant row is above; quarters are correlated repeat samples.
            quarter=times.dt.to_period('Q')
            for qlabel in sorted(quarter.dropna().astype(str).unique()):
                mask=(quarter.astype(str)==qlabel).to_numpy(bool)
                if int(mask.sum())<1100: continue
                x.process('D09_'+ident+'_'+qlabel,'D09_Brazil_quarter','Brazil/'+str(info['brazil_federative_unit']),'quarter subset of same publisher-aggregated plant WMA series, correlated repeat',q[mask],times.loc[mask].reset_index(drop=True),int(mask.sum()),metadata={'source_site_identity':ident,'source_quarter':qlabel,'brazil_federative_unit':str(info['brazil_federative_unit']),'structure_type':str(info['structure_type']),'nominal_power_mw':float(info['nominal_power_mw']),'source_records_processed_WMA':True,'has_temperature_interpolation_flag_column':bool('interpolated_keys_panel_temperature_celsius' in df.columns)},sensitivity=True,min_n=1000,min_days=30)
            if i%10==0:print('BRAZIL PROGRESS',i+1,'/',len(files))
    export_csv(out/'country_source_support_gates.csv',x.source_gate)
    wrows=[]
    for ident,w in x.weights.items():
        wrows.append({'target_id':ident,**{f'node_{j:02d}_G{int(g)}_T{int(t)}':float(w[j]) for j,(g,t) in enumerate(ns['xy'])}})
    export_csv(out/'original_grid_27_node_site_weights.csv',wrows)
    export_csv(out/'external_source_order_replay.csv',x.summary)
    export_csv(out/'external_pairlevel_decisions.csv',x.pairs)
    df=pd.DataFrame(x.summary)
    prim=df[(df.source_order!='Target-local heuristic') & (~df.is_repeated_sensitivity)]
    smry={ 'baseline':parity,'original_script_SHA256':sha(code),'input_source_sha256':hashes,'n_target_trajectories_all_non_hold':len(x.sites),'target_ids':x.sites,'n_held_pair_records':len(x.pairs),'n_source_order_rows':len(x.summary),'scientific_scope':'Stage A source-conditioned order transport only; original nine-product response matrices unchanged; input field series supply G/T states, not physical product labels','main_old_source_orders':list(x.names),'preanalysis_spec':'PROJECT_66_PREOUTCOME_PROTOCOL_REGISTER','new_external_site_groups':{'Germany':'3 instrument/system seasonal trajectories (one regional climate)','Italy':'1 site, primary inv1; inv2/inv3 and annual slices as repeated sensitivities','Brazil':'51 field files, only those passing n>=1000 & day>=30 eligibility'},'processed_source_claim_caveat':'Brazil WMA and unflagged positive sample counts, not source-native logger; German minute-resampled; Italy 15-min means','primary_source_best_counts':prim.groupby('target_id',group_keys=False).apply(lambda y:y.sort_values('directional_excess_pct_all_resolved_only',na_position='last').head(1).source_order.iloc[0],include_groups=False).value_counts().to_dict() if len(prim) else {},'primary_wrong_sum':int(prim.n_wrong_accepted.sum()),'primary_unresolved_sum':int(prim.n_unresolved.sum()),'safe_for_global_claim':False}
    (out/'external_summary.json').write_text(json.dumps(smry,indent=2,default=str)+'\n',encoding='utf-8')
    print('FINAL',json.dumps({k:smry[k] for k in ['n_target_trajectories_all_non_hold','n_held_pair_records','n_source_order_rows','primary_source_best_counts','primary_wrong_sum','primary_unresolved_sum']},indent=2))
if __name__=='__main__':main()
