# Stage B — exact-unit shortlist arithmetic

This additional lightweight audit reproduces the **11 physical-module unit** Cocoa–Eugene annual final-yield table and q=5% shortlist diagnostic reported in the manuscript. It uses numeric table values only; raw logger records are **not** included. The original experiment is Marion, Deceglie & Silverman, *Solar Energy* 110 (2014) 736–744, DOI 10.1016/j.solener.2014.10.017.

Run `python stageB_derived_audit/reproduce/verify_shortlists.py` from any working directory. The script verifies 2 source-retained units, 5 target-relevant units, three false exclusions, 40% coverage, ten nonempty forward intervals, and no reverse false-exclusion interval.

**Boundary:** The separate Oslo–Tozeur–Sevilla matched-configuration demonstration uses a different public raw archive and is not replayed by this table-only check. This is not exact-unit redeployment at those later sites.
