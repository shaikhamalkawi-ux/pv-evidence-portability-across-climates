# Reviewer quick-start

This repository accompanies the manuscript *Directional Portability of PV Characterization Sequences: Measurement Burden and Shortlist Exclusion Across Climates*.

Two verification routes are available.

## Fast check from included derived records

```bash
python -m pip install -r requirements-verify.txt
bash run_checks.sh
python stageB_derived_audit/reproduce/verify_shortlists.py
```

Expected: Stage-A derived-output verification **26/26 PASS**; Stage-B exact-unit Cocoa/Eugene check reproduces 2 source-retained units, 5 Eugene-relevant units, 3 false exclusions at q=5%, 40% target-set coverage and 10 nonempty forward intervals.

## Inspect or replay the original Stage-A algorithm

The recovered original Stage-A source programs are public in `code/stageA_original/`.

Start with:

`code/stageA_original/README.md`

The public directory contains the exact five-environment replay code, core characterization-depth code, locked-result verifier, Switzerland input manifest and recorded environment. A full raw-to-result execution requires reacquiring the original third-party inputs from the producer repositories listed in `THIRD_PARTY_DATA.md`; raw producer files are not re-hosted here.

The distinction is deliberate: **the analysis code is public; third-party raw data redistribution is not implied.** The same code was freshly rerun from the project-held producer files on 18 October 2026; the resulting four primary tables were byte-identical to the frozen outputs and the output verifier passed 26/26 checks. See `qa/RAW_TO_RESULT_REPLAY.md` and `qa/FRESH_RAW_TO_RESULT_REPLAY_20261018.json`.

## Deeper archive checks

The separately preserved SHA-locked complete replay archive previously passed **188/188** full-campaign workload checks and **5,400/5,400** sequential-information checks. These are computational verification counts, not independent physical experiments or metrological trials.

## Claim boundaries

This repository does not provide a certified measurement-uncertainty budget, measured laboratory-time savings, a universal characterization subset or a universal procurement rule. Stage A concerns source-sequence/target-support transport; Stage B concerns shortlist exclusion. Keep those endpoints separate.
