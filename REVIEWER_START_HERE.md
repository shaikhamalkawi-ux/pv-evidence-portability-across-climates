# Reviewer quick-start — public code and derived results

**GitHub archive steward: Ghassan Malkawi.** This is a data/code companion for the journal manuscript *Directional Portability of PV Characterization Sequences: Measurement Burden and Shortlist Exclusion Across Climates*. The official manuscript author list is independent from this GitHub archive-steward role.

The current derived-data scripts can be audited without privileged access or downloading producer raw logger records. From a fresh checkout:

```bash
python -m pip install -r requirements-verify.txt
bash run_checks.sh
```

Expected: original Stage-A derived-output verification **26/26 PASS**; exact physical-unit Stage-B source/target shortlist: Cocoa 2 retained, Eugene 5 retained, 3 false exclusions at q=5%, 40% target-set coverage and 10 nonempty forward exclusion intervals. The larger R4 scientific archive (not redistributed here) is needed for the separate 188/188 campaign-cost and 5,400/5,400 sequential shadow-mode checks; see README and SOURCE_SCRIPT_SHA256.json for provenance.

**What is not available here:** large raw third-party logger data, an author-identified journal manuscript PDF, a certified measurement uncertainty budget, measured laboratory-time savings, or a universal procurement claim. Sources are cited under THIRD_PARTY_DATA.md; get original raw files from the cited producers under their terms.

Repository is public for peer review; no license to modify/redistribute this project's code is granted until a separate explicit license is published. GitHub accessibility does not replace source attribution or rights verification.
