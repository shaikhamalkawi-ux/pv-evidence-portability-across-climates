# Reviewer access and scope

This public repository provides three levels of reproducibility support for the manuscript.

1. **Included derived-result checks.** `verify_derived_only.sh` reconstructs the archived independent Stage-A output assertions, and `stageB_derived_audit/reproduce/verify_shortlists.py` reproduces the Stage-B exact-unit Cocoa/Eugene table calculation.

2. **Original Stage-A implementation.** The recovered byte-verified source programs are public under `code/stageA_original/`, including `reproduce_characterization_depth.py`, `directional_transfer_5site.py`, `verify_r12.py`, the Task-13 monthly-file manifest, and the recorded environment. These are the original computational programs used for the locked Stage-A five-environment analysis.

3. **Raw-data replay.** A fresh raw-to-result execution requires original third-party data from the producer repositories listed in `THIRD_PARTY_DATA.md`. Those raw producer files are intentionally not redistributed here. The public code therefore closes the code-availability gap while preserving source-data rights and provenance boundaries.

The preserved author-controlled R4 archive, SHA-256
`cca1db15a2b76011401099aa128e47d87552093d94248d6a4d5c35e16ff06d1b`,
also contains the deeper campaign-workload and sequential-information audit material. Prior locked checks report 188/188 full-campaign workload comparisons and 5,400/5,400 sequential-information matches.

No claim is made that this repository supplies a calibrated measurement-uncertainty budget, measured laboratory-time savings, or raw measurements of the nine response-panel products at the external field sites.
