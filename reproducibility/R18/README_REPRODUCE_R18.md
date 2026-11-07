# Project 66 — R18 Frozen-Ledger Reproducibility Route

This is a derived-record audit of the **frozen R16/EP9R9** decision ledger, not a new physical measurement or a substitute for the producer raw-data workflow.

## Inputs

- `R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv` — 190 historical source-order/target rows, with exact numeric comparison fields and correctness flags.
- `R16_COMPLETE_VALIDITY_GATED_CENSUS.csv` — independent R16 classification of the 190 comparisons.

Both input files are copied unchanged from the frozen R16 package. Their exact SHA-256 identities are stored in `R18_MAGNITUDE_QA.json`.

## Reproduction (Python 3 standard library)

Run these commands in the same folder as the files:

```bash
python verify_R16_validity_gate.py
python derive_R18_magnitude_audit.py
```

The first command independently reconstructs **190 / 188 / 184 / 16 / 4 / 12**, checks the 184-run 3x3 validity-gated table, and verifies the m=2 identity. It reproduces the R16 census **byte-for-byte**. The second command derives the full-precision 12-case table used to format Supplementary Table S14 and asserts:

- 12 valid strict task reversals among 184 correct/complete runs.
- 11 distinct targets, with **9 Brazil / 2 Germany / 1 Italy** run-level rows.
- 9 changes of only 1 visited test cell in winner depth.
- All 12 absolute mean-depth percentage differences below 5%; maximum 4.86111111...%.

The scripts fail closed if any required identity, denominator, source record or data direction is inconsistent. No bootstrap, significance test, stochastic sampling, interpolation, raw curve or new PV experiment is performed here.

## Interpretation boundary

These rows are repeated algorithmic replays of a shared product-response panel and correlated source records, not 12 independent climates or independent statistical trials. Correctness of an accepted winner is checked against the full reference *after* stopping. Neither this audit nor its absence of some errors establishes a prospective safety certificate, universally optimal test sequence or measured savings in laboratory minutes.

`R18_VALIDITY_GATED_12_CASE_MAGNITUDES.csv` preserves complete source identifiers and full precision. The typeset Table S14 abbreviates geographic family prefixes and rounds percentages for readability only.

To reproduce all original historical results from producer observations, obtain the separate source-locked raw inputs under producer rights and run the original Stage A code, which is **not** replaced by this derived-only check. The GitHub companion at https://github.com/shaikhamalkawi-ux/pv-evidence-portability-across-climates remains a historical code/derived-results record; do not assume that this R18 check is already uploaded there.
