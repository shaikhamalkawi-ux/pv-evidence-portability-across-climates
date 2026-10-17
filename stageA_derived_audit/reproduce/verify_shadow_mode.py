#!/usr/bin/env python3
"""Independent pair-wise information-availability replay of archived Global Solar Stage A.

Requires ONLY the exact locked R4 public-derived source ZIP; no measured laboratory
activity or simulated measurement uncertainty is claimed.  Full test-pair response is
not an input to the stopping function. It is used only afterward for truth labeling.
"""
import argparse,hashlib,io,itertools,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd

SOURCE_SHA = 'cca1db15a2b76011401099aa128e47d87552093d94248d6a4d5c35e16ff06d1b'
N_PAIRS=36; N_PRODUCTS=9

def calibrated_stop(other_pairs_full, other_pairs_partial, held_pair_partial):
    """Only seven OTHER known module profiles + revealed held-pair prefix may enter.

    Arrays: (21,) calibration full differences, (21,k) calibration partial
    prefixes and (k,) revealed held-pair partial prefixes.  No held-pair
    full-target comparison is accepted as a function argument.
    """
    residual=np.max(np.abs(other_pairs_full[:,None]-other_pairs_partial),axis=0)
    eligible=np.flatnonzero(np.abs(held_pair_partial)>residual) # STRICT >
    if len(eligible)==0: return None
    return int(eligible[0])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('original_r4_zip',type=Path)
    parser.add_argument('--output-dir',type=Path,default=Path('verified_shadow'))
    opt=parser.parse_args()
    sha=hashlib.sha256(opt.original_r4_zip.read_bytes()).hexdigest()
    assert sha==SOURCE_SHA, f'BLOCK: original R4 ZIP hash mismatch: {sha}'
    with zipfile.ZipFile(opt.original_r4_zip) as z:
        assert z.testzip() is None
        weights=pd.read_csv(io.BytesIO(z.read('results/original_grid_27_node_site_weights.csv')))
        archived=pd.read_csv(io.BytesIO(z.read('results/external_pairlevel_decisions.csv')))
        with zipfile.ZipFile(io.BytesIO(z.read('R3_ARCHIVED_BASELINE/Original_R3_COMPLETE_20260901.zip'))) as z2:
            with zipfile.ZipFile(io.BytesIO(z2.read('Stable_PV_Comparisons_Do_Not_Guarantee_Portable_Evidence_Reproducibility.zip'))) as z3:
                mat=pd.read_csv(io.BytesIO(z3.read('Stage_A_Characterization_Order/data/sandia_iec61853_performance_matrix_long.csv')))
    coordinates=mat[['irradiance_Wm2','temperature_C']].drop_duplicates().sort_values(['irradiance_Wm2','temperature_C']).reset_index(drop=True)
    xy=coordinates[['irradiance_Wm2','temperature_C']].to_numpy(float)
    ids=sorted(mat.module_id.unique());assert len(ids)==N_PRODUCTS and len(xy)==27
    Z=np.zeros((len(ids),len(xy)))
    for i,m in enumerate(ids):
        x=coordinates.merge(mat[mat.module_id==m],on=['irradiance_Wm2','temperature_C'],how='left')
        pstc=float(x.loc[(x.irradiance_Wm2==1000)&(x.temperature_C==25),'Pmp_W'].iloc[0])
        assert np.isfinite(pstc) and pstc>0
        Z[i]=x.Pmp_W.to_numpy(float)/pstc
    stc=int(coordinates.index[(coordinates.irradiance_Wm2==1000)&(coordinates.temperature_C==25)][0])
    pairs=list(itertools.combinations(range(len(ids)),2)); assert len(pairs)==N_PAIRS
    pi={pair:i for i,pair in enumerate(pairs)}
    cal_index=[]
    for a,b in pairs:
        others=[j for j in range(N_PRODUCTS) if j not in {a,b}]
        cal_index.append([pi[j] for j in itertools.combinations(others,2)])
        assert len(others)==7 and len(cal_index[-1])==21
    archived=archived[archived.source_order=='Target-local heuristic'].copy()
    assert len(archived)==len(weights)*N_PAIRS
    results=[]
    for _,x in weights.iterrows():
        target=x.target_id
        w=x.iloc[1:].to_numpy(float)
        assert np.all(np.isfinite(w)) and np.min(w)>=-1e-11 and abs(w.sum()-1)<1e-9
        order=np.asarray(sorted([j for j in range(len(xy)) if j!=stc and w[j]>1e-14],key=lambda j:(-w[j],xy[j,0],xy[j,1])),int)
        assert len(order)>0
        # Fully observed CALIBRATOR products only; all pairs are traversed as leave-two-out cases.
        node_contrib=np.vstack([w*(Z[a]-Z[b]) for a,b in pairs])
        full_contrasts=node_contrib.sum(axis=1)
        partials=np.cumsum(node_contrib[:,order],axis=1)
        for p,(a,b) in enumerate(pairs):
            other=cal_index[p]
            cut=calibrated_stop(full_contrasts[other],partials[other,:],partials[p,:])
            n_cells=int(cut+2) if cut is not None else None # STC + non-STC prefix
            # The following is a POST-HOC label only, not passed to the stopping function.
            wrong=bool(cut is not None and np.sign(partials[p,cut])!=np.sign(full_contrasts[p]))
            results.append(dict(target_id=target,module_a=ids[a],module_b=ids[b],stop_cells=n_cells,unresolved=cut is None,wrong_accepted=wrong))
    got=pd.DataFrame(results)
    compare=got.merge(archived[['target_id','module_a','module_b','stop_cells','unresolved','wrong_accepted']], on=['target_id','module_a','module_b'],validate='one_to_one',suffixes=('_new','_archived'))
    assert len(compare)==5400
    assert np.array_equal(compare.stop_cells_new.fillna(-1).to_numpy(),compare.stop_cells_archived.fillna(-1).to_numpy())
    assert np.array_equal(compare.unresolved_new.to_numpy(),compare.unresolved_archived.to_numpy())
    assert np.array_equal(compare.wrong_accepted_new.to_numpy(),compare.wrong_accepted_archived.to_numpy())
    assert len(set(got.target_id))==150
    output={
      'status':'PASS', 'input_locked_source_sha256':sha, 'targets':150,
      'sequential_pairwise_decisions':len(got), 'pair_specific_calibration_products':7,
      'calibration_pairs_excluding_held_pair':21,
      'baseline_reference_comparison':'target-local heuristic',
      'stop_depth_exact_matches':len(got),'unresolved_flag_exact_matches':len(got),
      'wrong_accepted_flag_exact_matches':len(got),
      'held_pair_full_contrast_used_to_stop':False,
      'held_pair_full_contrast_used_afterward_to_label_errors':True,
      'physical_experiment':False,'lab_time_or_uncertainty_validated':False,
      'note':'Leave-two-products-out calibration rotates with each evaluated pair. 150 targets and 5400 paired replay records share the same 9-product response panel and are NOT independent physical site experiments.'}
    opt.output_dir.mkdir(parents=True,exist_ok=True)
    (opt.output_dir/'shadow_mode_summary.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    # Save only representative (one per target) information disclosure summary, not full target data.
    summary=got.groupby('target_id').agg(n_pairs=('module_a','size'),n_unresolved=('unresolved','sum'),n_wrong=('wrong_accepted','sum'),max_stop_cells=('stop_cells','max'),mean_stop_cells=('stop_cells','mean')).reset_index()
    summary.to_csv(opt.output_dir/'shadow_mode_target_summary.csv',index=False)
    print(json.dumps(output,indent=2))

if __name__=='__main__': main()
