# Original Stage-A replay source

This directory exposes the recovered, byte-verified Stage-A source programs used for the locked five-environment characterization-order analysis. The code is published for reviewer inspection and replay; third-party producer data are not redistributed here.

## Exact source identities

- `directional_transfer_5site.py` — SHA-256 `79ec83a814a0f665c310d75de42c40471e9491f4ca09f1d54f1ad26b5b8eddc9`
- `reproduce_characterization_depth.py` — SHA-256 `bf1fa4e7d7c8784b0f140ef4f55a412e1a04857409058479ed0585b290fafdff`
- `verify_r12.py` — SHA-256 `26d6cbb6822de3b557bbfd4905510316ee035656dae3028488f537313cac2c7e`
- `SWITZERLAND_REQUIRED_FILES.csv` — exact filenames, row counts and SHA-256 values for the 12 Task-13 monthly CSVs.
- `environment.txt` — recorded execution environment for the recovered source.

These files were recovered from the preserved R3/R12 scientific archive. No calculation rule was rewritten for this public release.

## What is needed for a full replay

The scripts expect the original third-party inputs in the same structure as the archived program:

- `data/sandia_iec61853_performance_matrix_long.csv`
- `mpert_core/*.csv` for the 15 NREL mPERT core trajectories
- the 12 IEA Task-13 monthly CSVs listed in `SWITZERLAND_REQUIRED_FILES.csv`
- Sandia `tmod_sample_data.nc`, expected SHA-256:
  `a934d40671063ee2a8666ee133c612390f7f1a339549fdc77159b81efdd5abd7`

Obtain those data from the original producer repositories listed in the root `THIRD_PARTY_DATA.md` and comply with their licences. This repository intentionally does not re-host those raw producer files.

## Replay the core U.S. characterization analysis

After placing the response matrix and mPERT files under the paths above:

```bash
python code/stageA_original/reproduce_characterization_depth.py
```

This constructs the original Stage-A characterization-depth outputs from the response matrix and U.S. operating-state records.

## Replay the five-environment directed matrix

After also obtaining the Task-13 monthly files and the Sandia Albuquerque NetCDF:

```bash
python code/stageA_original/directional_transfer_5site.py \
  --task13-dir /path/to/task13_monthly_csvs \
  --albuquerque-nc /path/to/tmod_sample_data.nc \
  --output-dir /path/to/output
```

The program builds target operating-state weights, fixed source orders, all 25 directed source-target transfer cells, pair-level decisions, common-support checks, pooled/LOCO comparators, technology-stratified sensitivity, random-order references and symmetric-distance diagnostics.

## Locked-result verification

`verify_r12.py` verifies the archived locked outputs when they are placed in the original `outputs/r12_directional/` location. It checks 17 named result conditions including all 25 transfer cells, zero aggregate unresolved/wrong-accepted counts in the five-site matrix, the locked directional values, source portfolios and pooled-sequence summary.

## Scope

This public source closes the distinction between **code availability** and **raw-data redistribution**. The complete Stage-A computational implementation is public. A fresh raw-to-result replay still requires the original third-party input files from their producers. The absence of those raw bytes from this repository is a data-rights/provenance boundary, not missing analysis code.

The empirical stopping envelope is not a calibrated measurement-uncertainty model, and this code does not create a metrological confidence guarantee or measured laboratory-time saving.
