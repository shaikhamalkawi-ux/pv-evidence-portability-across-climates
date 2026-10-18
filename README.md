# PV Evidence Portability Across Climates

**Code and derived-result companion** to the Global Solar research manuscript:

*Directional Portability of PV Characterization Sequences: Measurement Burden and Shortlist Exclusion Across Climates*

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
