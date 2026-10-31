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

## Separate support-geometry reproducibility package (Solar Compass MR4)

Supplementary Table S7 has an additional author-provided reviewer ZIP, `SolarCompass_TableS7_Reviewer_Code_And_Derived_Data_NoRaw.zip`, to be uploaded as a separate journal supplemental file. It contains `support_exclusion_audit.py`, the fixed 27-node grid, the frozen support-gate registry, 40-target derived geometry outcomes, manifests, a replay verifier, and source acquisition notes. It does **not** redistribute producer-owned logger files, and it is **not** part of this public repository's derived-only replay script. Reviewers should use the manuscript supplemental upload, not assume that S7 can be reproduced from this GitHub checkout alone.

The current manuscript is a 31 October 2026 **Solar Compass** author-review candidate, not an IEEE OJIM submission or a published article. MR4 adds clear source-verified chronological deployment limitations for Cocoa and Eugene and explicit within-grid conditioning; it makes no new calculation or experimental validation claim. The frozen reproducibility-code snapshot cited by MR4 is `9a8dea54c5ec266d7d3c995fc73b61bb08f5bc60`.

## Claim boundaries

This repository does not provide a certified measurement-uncertainty budget, measured laboratory-time savings, a universal characterization subset or a universal procurement rule. Stage A concerns source-sequence/target-support transport; Stage B concerns shortlist exclusion. Keep those endpoints separate.
