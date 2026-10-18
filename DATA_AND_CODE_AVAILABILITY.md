# Reviewer access and scope

This public repository provides three levels of reproducibility support for the manuscript.

1. **Included derived-result checks.** `verify_derived_only.sh` reconstructs the archived independent Stage-A output assertions, and `stageB_derived_audit/reproduce/verify_shortlists.py` reproduces the Stage-B exact-unit Cocoa/Eugene table calculation.

2. **Original Stage-A implementation.** The recovered byte-verified source programs are public under `code/stageA_original/`, including `reproduce_characterization_depth.py`, `directional_transfer_5site.py`, `verify_r12.py`, the Task-13 monthly-file manifest, and the recorded environment. These are the original computational programs used for the locked Stage-A five-environment analysis.

3. **Raw-data replay.** A fresh same-code raw-to-result replay was executed from the project-held producer files on 18 October 2026. It reproduced the original 25/25 baseline cells and regenerated four primary output tables byte-for-byte identically to the frozen archive: 230 support-gate rows, 150 target-weight rows, 900 transfer rows and 32,400 pair decisions; the separate output verifier passed 26/26 checks. Third parties can repeat this route after reacquiring the original producer files listed in `THIRD_PARTY_DATA.md`; those raw producer files are intentionally not redistributed here.

The preserved complete replay archive, SHA-256
`cca1db15a2b76011401099aa128e47d87552093d94248d6a4d5c35e16ff06d1b`,
also contains the deeper campaign-workload and sequential-information audit material. Prior locked checks report 188/188 full-campaign workload comparisons and 5,400/5,400 sequential-information matches.

No claim is made that this repository supplies a calibrated measurement-uncertainty budget, measured laboratory-time savings, or raw measurements of the nine response-panel products at the external field sites.
