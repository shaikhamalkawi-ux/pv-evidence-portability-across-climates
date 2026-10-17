# PV Evidence Portability Across Climates

**Code and derived-result companion** to the Global Solar research manuscript:

*Directional Portability of PV Characterization Sequences: Measurement Burden and Shortlist Exclusion Across Climates*

**Repository maintainer and GitHub code-archive contact: Ghassan Malkawi** (sole maintainer). This public code and derived-results companion corresponds to Global Solar **Project 66, scientific R4** (author-identified manuscript prepared 18 October 2026). Journal-manuscript authorship is recorded in the paper separately; GitHub repository maintainer credit must not be substituted for the paper byline. No final journal DOI exists; this repository is **not** evidence of journal acceptance.

## What does this repository test?

We examine two **different** PV evidence-transfer operations, without conflating them:

- **Stage A — characterization sequence transfer:** does a measurement test-condition order derived for one climate lead to additional or fewer irradiance–temperature test cells when applied to another climate's observed operating-state distribution? The supplied derived output tables cover the original five-site evidence and separately admitted field-state replays in Germany, Italy and Brazil. The Safi Morocco raw-synchronization audit remains a separately reported conditioning case. The nine original response-panel products were **not measured** at these external sites.
- **Stage B — shortlist transfer:** does a source-climate candidate shortlist exclude exact physical modules that remain target relevant? The included small self-contained script reproduces the published 11-unit Cocoa/Eugene q=5% case. The independent Oslo/Tozeur/Sevilla matched-configuration field results are cited in the manuscript but require the original producer archive for independent raw reconstruction.

**The core engineering result is conditional**: A low mean pairwise stopping depth does not necessarily lower full-campaign burden. Neither the computational stopping rule nor the workload proxies are measured test duration, measurement uncertainty or IEC compliance certificates.

## Verify outputs without downloading raw producer archives

Python 3 with `numpy` and `pandas` is needed for Stage A. Stage B's small exact-unit check uses standard-library Python.

```bash
python -m pip install -r requirements-verify.txt
bash verify_derived_only.sh
python stageB_derived_audit/reproduce/verify_shortlists.py
```

Expected: **26/26** independently reconstructed frozen Stage-A output checks PASS; Stage-B **3/5** target-relevant units excluded by source, 10 forward nonempty exclusion intervals. In the source archive, Stage-A campaign workload cross-checks are **188/188** and the pair-specific information-flow replayer is **5,400/5,400** exact matches; these two deeper tests require the original SHA-locked author-controlled archive. Do not portray the field target records as independent experiments or confidence samples.

## Structure

| Path | Description |
|---|---|
| `code/` | Frozen Stage-A multicountry replay, derived-output verifier and figure builder |
| `results/` | Derived Stage-A decision, support and summary tables (not producer logger measurements) |
| `stageA_derived_audit/` | Campaign proxy recomputation and pair-specific shadow-mode verification |
| `stageB_derived_audit/` | Auditable 11-unit Cocoa–Eugene final-yield shortlist calculation |
| `derived_inputs/` | Small Safi conditional diagnostic (not a new field site) |
| `qa/` | Independent output verification ledger |
| `SOURCE_SCRIPT_SHA256.json` | Frozen source hashes; source R4 master requires separate local access |
| `THIRD_PARTY_DATA.md` | Official producer citations, provenance and rights guardrails |
| `SCOPE_AND_RESULTS.md` | Claim boundaries; differences between computed and physical observations |

## Full retrospective replay (optional, requires frozen historical archive)

The current repo does **not** redistribute the entire original `Project62_R4_Multicountry_Reproducibility.zip` or any raw third-party logger datasets. The exact historical archive SHA-256 is:

`cca1db15a2b76011401099aa128e47d87552093d94248d6a4d5c35e16ff06d1b`

If this exact authorized archive is already available locally, run:

```bash
bash stageA_derived_audit/verify_all.sh /absolute/path/to/Project62_R4_Multicountry_Reproducibility.zip
```

That reproduces the engineering counts and Stage-A information-flow audit without tuning or altering baseline results. Before repeating any raw source acquisition, obtain the publisher source releases at the original DOIs and honor source licences and citation requirements.

## Data rights and scientific limitations

This repository contains **code and compact derived data only**. It does not host NREL, Sandia, IEA, Zenodo, Mendeley or other producer logger datasets; see `THIRD_PARTY_DATA.md`. Check the source licence and attribution before redistributing derivative tables. Public accessibility does not constitute an open-source licence: unless a later explicit licence is added, code reuse requires the rights holder's permission.

No unobserved field performance, laboratory-time savings, probabilistic error rate, source-product causal mechanism, or universal shortlisting safety is claimed. The paired source–target diagnostics are direction-specific and stage-specific, not universal product procurement recommendations.
