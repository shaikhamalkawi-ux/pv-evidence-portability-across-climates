> **Current public review update (8 November 2026):** Reproducibility materials for the R18 validity-gated task-reversal audit are in [reproducibility/R18](reproducibility/R18), with a reproducible, source-hash-gated magnified figure in [figures/R19](figures/R19). The underlying 190-row decision ledger and 12-case table are derived records, not third-party raw PV measurements or an independent prospective experiment. These public files do not establish measured lab-time savings or a calibrated risk bound. The manuscript's MDPI-specific author-review template is kept outside this public repository. The complete **journal-neutral R19 working manuscript and supplement PDFs**, plus a source ZIP without the publisher template, are now in [preprint/](preprint/). These PDFs are not accepted journal articles.\n\n# PV Evidence Portability Across Climates

The **R21 journal-neutral author-review manuscript, full Supplementary PDF and public LaTeX** are in [preprint/R21](preprint/R21). The publisher-specific MDPI template remains outside the public GitHub repository. No peer review, acceptance, publisher DOI or prospective measurement validation is implied.

**R21 mathematical explanation (14 November 2026).** The [R21 derived graph audit](reproducibility/R21/README.md) decomposes the same 36 pair-depth edges into an eight-edge correct-winner star and 28 other edges, with source-hash-gated independent checks for the 12 retrospectively valid task reversals. A Pareto appendix compares only the six tested orders. No new original PV measurements, physical cost experiment or prospective decision certificate is claimed.

**R20 preference-space interpretation (derived-only, 14 November 2026).** The [R20 reproducer](reproducibility/R20/README.md) classifies 79 historical replays into 34 all-positive-weight improvements, 30 all-positive-weight deteriorations and 15 weight-sensitive cases. Fuzzy alpha-cuts and shortlist-tolerance profiles are illustrative **decision preferences**; no instrument uncertainty, measured cost ratio, expert elicitation or prospective validation is claimed. This is a bounded interpretation of unchanged R19 response and decision data.

**Code and derived-result companion** to the current Project 66 working manuscript:

*Decision-Task Portability of PV Characterization Sequences: A Retrospective Cross-Climate Audit*

Historical archive title (preserved for provenance): *Directional Portability of PV Characterization Sequences: Measurement Burden and Shortlist Exclusion Across Climates*.

**Repository maintainer and GitHub code-archive contact: Ghassan Malkawi** (sole maintainer). Journal-manuscript authorship is recorded in the paper separately; repository maintenance is not the manuscript byline. No final journal DOI exists, and this repository is not evidence of journal acceptance.

## What does this repository test?

The manuscript evaluates two different evidence-transfer operations:

- **Stage A — characterization-sequence transfer:** whether a fixed measurement-condition order derived for one climate changes the number of irradiance-temperature test cells needed when applied to another climate's observed operating-state distribution.
- **Stage B — shortlist transfer:** whether a source-climate candidate shortlist removes exact physical modules or matched configurations that remain target relevant.

The central engineering result is conditional: a lower mean pairwise stopping depth does not necessarily reduce full-campaign workload, and a stable winner does not guarantee shortlist safety. The endpoints are decision-stage-specific and direction-specific.

## Reproducibility routes

### 1. Quick reviewer checks from included derived records

```bash
python -m pip install -r requirements-verify.txt
bash verify_derived_only.sh
python stageB_derived_audit/reproduce/verify_shortlists.py
```

Expected: **26/26** Stage-A derived-output checks PASS; Stage B reproduces the 11-unit Cocoa/Eugene 5% shortlist result with **3/5** target-relevant units falsely excluded and 10 nonempty forward false-exclusion intervals.

### 2. Original Stage-A computational implementation

The recovered original Stage-A source is now public under:

`code/stageA_original/`

It contains the byte-verified source programs:

- `reproduce_characterization_depth.py` — reconstructs the original Stage-A characterization-depth analysis from the response matrix and U.S. mPERT inputs.
- `directional_transfer_5site.py` — constructs the complete directed five-environment matrix after adding the public Switzerland and Albuquerque inputs.
- `verify_r12.py` — verifies the locked five-site result conditions.
- `SWITZERLAND_REQUIRED_FILES.csv` — filenames, row counts and SHA-256 identities for the 12 monthly Task-13 inputs.
- `environment.txt` — recorded software environment.

See `code/stageA_original/README.md` for exact input layout, commands and source hashes.

The computational implementation is therefore public. A fresh raw-to-result replay still requires the original third-party data files from their producers; this repository intentionally does not redistribute those raw bytes. A fresh same-code replay from the producer files was completed on 18 October 2026: the original 25/25 baseline cells were reproduced, four primary output tables were byte-identical to the frozen archive (230 support rows, 150 target-weight rows, 900 transfer rows and 32,400 pair decisions), and the independent output verifier again passed 26/26 checks. See `qa/RAW_TO_RESULT_REPLAY.md`.

### 3. Deeper frozen-archive audits

The preserved complete replay archive additionally passed **188/188** full-campaign workload checks and **5,400/5,400** pair-specific sequential-information checks. Those deeper checks use the SHA-locked archive:

`cca1db15a2b76011401099aa128e47d87552093d94248d6a4d5c35e16ff06d1b`

If an authorized copy of that exact archive is available locally:

```bash
bash stageA_derived_audit/verify_all.sh /absolute/path/to/Project62_R4_Multicountry_Reproducibility.zip
```

## Structure

| Path | Description |
|---|---|
| `code/stageA_original/` | Recovered original Stage-A raw-to-result source programs and input manifests |
| `code/` | Frozen multicountry Stage-A replay, derived-output verifier and figure builder |
| `results/` | Derived Stage-A decision, support and summary tables |
| `stageA_derived_audit/` | Full-campaign proxy recomputation and pair-specific shadow-mode verification |
| `stageB_derived_audit/` | Auditable 11-unit Cocoa-Eugene shortlist calculation |
| `derived_inputs/` | Small Safi conditional diagnostic |
| `qa/` | Independent output verification ledger |
| `SOURCE_SCRIPT_SHA256.json` | Source-code identities |
| `THIRD_PARTY_DATA.md` | Producer citations, provenance and rights guardrails |
| `SCOPE_AND_RESULTS.md` | Claim boundaries |

## Data rights and scientific limitations

No original NREL, Sandia, IEA, Zenodo, Mendeley or other producer logger data are redistributed here. Obtain them from the cited sources and comply with their licences. The field records provide operating-state distributions; they are not new field measurements of the nine response-panel products.

The empirical stopping envelope is not a calibrated measurement-uncertainty budget, the workload proxies are not measured laboratory time, and no universal safe sequence, error probability or procurement rule is claimed.


The **R20 journal-neutral working PDFs and editable LaTeX** are publicly readable in [preprint/R20](preprint/R20), separately from the author-review MDPI template. This is not a peer-reviewed or accepted paper.