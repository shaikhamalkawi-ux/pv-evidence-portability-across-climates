#!/usr/bin/env python3
"""Engineering workload diagnostic from *existing* Global Solar R4 pair-level replay.

Does not claim physical lab minutes, calibrated metrological safety, or IEC conformity.
Inputs: original Project62_R4_Multicountry_Reproducibility.zip on argv[1].
Produces bounded JSON and Markdown in requested output directory argv[2].
"""
import io, json, sys, zipfile, hashlib
from pathlib import Path
import pandas as pd

ORDERS=("Cocoa", "Eugene", "Golden", "Switzerland", "Albuquerque")
LOCAL="Target-local heuristic"

def main(src, out):
    src=Path(src); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(src) as z:
        assert z.testzip() is None, 'Archive CRC mismatch'
        pairs=pd.read_csv(io.BytesIO(z.read('results/external_pairlevel_decisions.csv')))
        runs=pd.read_csv(io.BytesIO(z.read('results/external_source_order_replay.csv')))
    assert pairs.shape==(32400,11),pairs.shape
    assert runs.shape==(900,21),runs.shape
    primary=runs[~runs.is_repeated_sensitivity].copy()
    assert len(primary)==228 and primary.target_id.nunique()==38
    assert primary.source_order.nunique()==6
    data=pairs.merge(primary[['target_id','source_order']],on=['target_id','source_order'],validate='many_to_one')
    assert len(data)==8208 # 38 * 6 * 36 pairs
    def workload(g):
        assert len(g)==36
        n_wrong=int(g.wrong_accepted.sum())
        n_unresolved=int(g.unresolved.sum())
        if n_unresolved:
            return dict(mean_cells=None,max_cells=None,module_cells=None,n_wrong=n_wrong,n_unresolved=n_unresolved)
        assert g.stop_cells.notna().all()
        assert g.stop_cells.ge(1).all() and g.stop_cells.le(27).all()
        k={(a,b):int(c) for a,b,c in zip(g.module_a,g.module_b,g.stop_cells)}
        assert len(k)==36
        mods=set(g.module_a)|set(g.module_b)
        assert len(mods)==9
        # Per-module latest test-cell index required by any pair involving it.
        # Idealized serial module×condition count; excludes repeats / stabilization / calibration.
        module_cost=sum(max(k[a,b] for a,b in k if a==m or b==m) for m in mods)
        return dict(mean_cells=float(g.stop_cells.mean()),max_cells=int(g.stop_cells.max()),module_cells=int(module_cost),n_wrong=n_wrong,n_unresolved=0)
    groups=[]
    for (t,s),g in data.groupby(['target_id','source_order']):
        groups.append(dict(target_id=t,source_order=s,**workload(g)))
    derived=pd.DataFrame(groups)
    assert int(derived.n_wrong.sum())==4
    assert int(derived.n_unresolved.sum())==3
    assert derived.module_cells.notna().sum()==226
    refs=derived[derived.source_order==LOCAL].set_index('target_id')
    assert refs.module_cells.notna().all()
    hist=derived[derived.source_order.isin(ORDERS)].copy()
    assert len(hist)==190 and hist.module_cells.notna().sum()==188
    for col in ['mean_cells','max_cells','module_cells']:
        hist['ref_'+col]=hist.target_id.map(refs[col])
        hist['excess_'+col]=100*(hist[col]/hist['ref_'+col]-1)
    complete=hist[hist.module_cells.notna()].copy()
    # Independent finite denominators and sign-disagreement checks.
    n_mean_better=int((complete.excess_mean_cells < -1e-10).sum())
    n_mean_better_but_panel_worse=int(((complete.excess_mean_cells < -1e-10)&(complete.excess_module_cells>1e-10)).sum())
    n_mean_better_but_kmax_worse=int(((complete.excess_mean_cells < -1e-10)&(complete.excess_max_cells>1e-10)).sum())
    assert n_mean_better==79
    assert n_mean_better_but_panel_worse==26
    assert n_mean_better_but_kmax_worse==40
    set_discord_panel=0;set_discord_max=0
    for t,g in complete.groupby('target_id'):
        meanbest=set(g.loc[g.mean_cells <= g.mean_cells.min()+1e-10,'source_order'])
        mbest=set(g.loc[g.module_cells == g.module_cells.min(),'source_order'])
        kbest=set(g.loc[g.max_cells == g.max_cells.min(),'source_order'])
        set_discord_panel+=not bool(meanbest&mbest)
        set_discord_max+=not bool(meanbest&kbest)
    assert set_discord_panel==16
    assert set_discord_max==24
    ex=complete[(complete.target_id=='D09_PS_001')&(complete.source_order=='Albuquerque')].iloc[0]
    assert ex.mean_cells==258/36
    assert ex.ref_mean_cells==285/36
    assert ex.module_cells==102 and ex.ref_module_cells==100
    assert ex.max_cells==15 and ex.ref_max_cells==14
    # Published stop-depth (%) consistency cross-check from external replay.
    official=primary[primary.source_order.isin(ORDERS)].copy()
    chk=complete.merge(official[['target_id','source_order','directional_excess_pct_all_resolved_only']], on=['target_id','source_order'])
    assert (chk.excess_mean_cells-chk.directional_excess_pct_all_resolved_only).abs().max()<1e-8
    stats={
        'scientific_scope':'Retrospective, model-only laboratory-workload reinterpretation of existing R4 pair-level stopping outputs; not physical measurements and not IEC conformity',
        'archive_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'archive_file':src.name,
        'all_pairlevel_rows':len(pairs),
        'all_replay_rows':len(runs),
        'primary_field_state_targets':38,
        'primary_source_orders':len(ORDERS),
        'primary_historical_runs':190,
        'primary_historical_pairs':190*36,
        'historical_fully_resolved_runs':188,
        'historical_unresolved_pairs':3,
        'historical_wrong_accepted':4,
        'n_completed_historical_runs_mean_better_than_local':n_mean_better,
        'n_mean_better_but_panel_module_cells_worse':n_mean_better_but_panel_worse,
        'n_mean_better_but_max_k_worse':n_mean_better_but_kmax_worse,
        'n_targets_best_mean_vs_best_panel_disjoint':set_discord_panel,
        'n_targets_best_mean_vs_best_max_disjoint':set_discord_max,
        'example':{
            'target':'D09_PS_001 (Brazil/SP)',
            'source_order':'Albuquerque',
            'local_mean_cells':round(float(ex.ref_mean_cells),6),
            'source_mean_cells':round(float(ex.mean_cells),6),
            'mean_relative_pct':round(float(ex.excess_mean_cells),6),
            'local_campaign_max_conditions':int(ex.ref_max_cells),
            'source_campaign_max_conditions':int(ex.max_cells),
            'campaign_max_relative_pct':round(float(ex.excess_max_cells),6),
            'local_idealized_module_condition_measurements':int(ex.ref_module_cells),
            'source_idealized_module_condition_measurements':int(ex.module_cells),
            'module_condition_relative_pct':round(float(ex.excess_module_cells),6),
            'wrong_accepted_signs':int(ex.n_wrong),
            'unresolved':int(ex.n_unresolved),
        },
    }
    (out/'engineering_cost_audit.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    example=stats['example']
    report=f'''# Project 66 — Engineering application gate: evidence-to-lab workflow\n\nStatus: verified retrospective **derived analysis** (not in locked R4). No claim of real test-time savings, device safety, or IEC certification.\n\n## Audit from the original archived output\n\n- Original SHA-256: `{stats['archive_sha256']}`. ZIP CRC passes.\n- 38 primary Germany/Italy/Brazil field-state target distributions, 5 historical source orders = 190 runs = 6,840 pair decisions; 188 fully resolved runs. The 4 wrong accepted signs and 3 unresolved comparisons are the **same existing R4 evidence**.\n- A pair-level mean is not a laboratory-wide campaign count. For all 36 pairwise decisions on the same nine modules, idealized **distinct test-condition prefix** requires at least `max(k_ab)` positions for a common uniform sequence. A hypothetical per-module adaptive workflow requires `sum_i max_(j != i) k_ij` module×condition observations (excluding calibration, repeated scans, and preparation). Both are retrospective proxies, not measured labor or money.\n- Across 188 fully resolved historical runs, 79 have fewer mean pairwise cells than the target-local reference. Among those 79, **26 require more modeled module×condition observations**, while **40 require a longer common test-condition prefix**.\n- The historical order(s) minimizing mean pairwise depth share NO order with those minimizing modeled module×condition workload in **16/38 target distributions**; with those minimizing maximum prefix in **24/38**. Ties retained. These are descriptive counts across dependent field data, not sampling confidence claims.\n\n### Exact illustrated counterexample: Brazil D09_PS_001\n\n| Metric | Target-local reference | Albuquerque source order | Difference |\n|---|---:|---:|---:|\n| Mean pairwise stop cells | {example['local_mean_cells']} | {example['source_mean_cells']} | {example['mean_relative_pct']:+.3f}% |\n| Required common test-condition prefix (max over 36 pairs) | {example['local_campaign_max_conditions']} | {example['source_campaign_max_conditions']} | {example['campaign_max_relative_pct']:+.3f}% |\n| Idealized module×condition observations | {example['local_idealized_module_condition_measurements']} | {example['source_idealized_module_condition_measurements']} | {example['module_condition_relative_pct']:+.3f}% |\n\nThis shows why the source order may look cheaper in the paper's pair-mean metric but be **more costly for the full laboratory campaign under a different operational objective**. There were no wrong accepted signs/unresolved pairs in this example; safety and physical costs are still unvalidated.\n\n## Minimal action-ready engineering demonstration\n\n**Phase 0 — offline planning using existing R4 data (available now).** Define the intended decision unit (single pair versus all-module qualification campaign). Report four distinct outputs: (1) mean per-pair stop cells, (2) maximum common prefix to resolve all pairs, (3) modeled per-module exposure count, (4) wrong accepted/unresolved states and support fraction. A model-derived cheap order is not a 'safe' order in the laboratory.\n\n**Phase 1 — accredited full-matrix shadow validation.** Use identified physical modules with reproducible equipment traceability, controlled irradiance, multi-point module temperature measurement, calibrated reference sensor, I–V sweep, repeatability and stabilization logs. Measure **the full standards-required IEC 61853-1 matrix** for any certification claim. Only retrospectively run proposed source-order stop logic on that complete record and compare to the measured full-matrix reference; do NOT truncate mandatory tests.\n\n**Phase 2 — time and cost audit.** For each test condition and switch, log setup, ramp and thermal stabilization, I–V acquisitions, repeats and QA aborts. Compare genuine total wall-clock and energy use under controlled matched sequences, allowing for order-induced thermal transients. Costs and time cannot be inferred from number of cells alone.\n\n**Phase 3 — evidence of correct decisions.** Use instrument and correction uncertainty evaluated from the actual lab metrological chain (e.g., simulator IEC 60904-9 and I–V correction IEC 60891). Predefine indeterminate handling for near-tied pairs, remeasurements and source/target support gates. An empirical R4 residual envelope is not a calibrated confidence interval, so a zero-error replay would still not establish a universal safety probability.\n\n**Phase 4 — Stage B field validation (separate).** If physical modules/versions are deployed cross-climate, preserve *exact* unit identities or clearly label matched configurations. Measure matched annual yield/normalized power, and compare target shortlist membership against the source shortlist at a prospectively registered resolution; do not treat this as a measurement-time endpoint.\n\n## Mandatory guards\n\n- The archived 27-node computational grid is NOT by itself a demonstration of compliance with the entire IEC 61853 testing protocol.\n- Avoid claiming 36 independent field replications: they are 36 product pairs; plant/quarter time windows are dependent.\n- A validated physical PV matrix for the nine exact archived response products is unavailable from the new countries; they provide environmental state weights, not nine-product field power.\n- For the first live pilot, the facility must identify which products and accredited instrumentation are available; model-derived results remain historical until a real test rig executes them.\n- This analysis is a prospective improvement candidate; scientific manuscript R4 remains unchanged until author-side decision and complete review.\n\n## Standards / context\n\nIEC 61853-1 official: https://webstore.iec.ch/en/publication/6035\n\nIEC 60904-9 official (solar simulator): https://webstore.iec.ch/en/publication/28973\n\nIEC 60891 official (I–V correction): https://webstore.iec.ch/en/publication/61766\n'''
    (out/'engineering_application_gate.md').write_text(report,encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':
    if len(sys.argv)!=3: sys.exit('usage: python engineering_cost_audit.py ORIGINAL_R4_ARCHIVE.zip OUTPUT_DIR')
    main(sys.argv[1],sys.argv[2])
