# Nominal shortlist-transfer diagnostic

A small, standard-library-only implementation of the shortlist definitions used in the Project 66 photovoltaic evidence-portability study. This is a code-review addition, not a new empirical result or a journal/software release.

`shortlist_transfer.py` is byte-identical to the implementation delivered in the private R11 matched-cohort toolkit (SHA-256 `d101f556f4e048f394e1a39ed1c45862517b55a3f0e0a44ba2b893a47bfbf257`). The new tests use synthetic values only. No measured producer data, laboratory workbook, frozen climate weights, private manuscripts, or restricted source archives are included in this directory.

## Input and scientific scope

Supply a UTF-8 CSV with a `module` column and two named positive-endpoint columns. Every retained identifier must refer to the scientifically comparable candidate intended by the study. The program checks input syntax, positivity, duplicates and cohort selection; it cannot establish physical identity, comparable units, representative periods or measurement quality.

For candidate i and site c, the percentage deficit is `100 * (1 - Y[i,c] / max(Y[:,c]))`, computed within the declared cohort. At nonnegative cutoff q, retain candidates with deficit <= q. A nominal source-to-target false exclusion is a target-retained candidate missing from the source set. For each such directional interval, the lower endpoint is included and the upper endpoint is excluded. Fraction arithmetic preserves equality for the supplied decimal values; it does not remove rounding or measurement uncertainty from those inputs.

## Run

From this directory, using Python 3.10 or later:

```bash
python -m unittest -v test_shortlist
python shortlist_transfer.py --input own_comparable_endpoints.csv --source Source --target Target --q 5 --output result.json
```

Run the second command again with source and target exchanged. Use `--exclude ID` only for an explicitly justified cohort restriction; exclusion changes the cohort maximum and is not an improvement of the method. The 12 tests include CLI checks, exact interval boundaries, ties, positive sitewise scaling, malformed inputs and cohort handling. They are implementation tests, not 12 physical experiments.

## Interpretation and release status

The output is a deterministic comparison of supplied point estimates. It is not an uncertainty-calibrated screening certificate, procurement recommendation, climate-causal estimate or optimal measurement schedule. This program implements Stage B only; it does not reproduce Stage A, the field integration or the complete manuscript.

The current manuscript remains under author review. No journal DOI, acceptance, software DOI or new license is asserted by this addition. Existing repository and third-party rights are unchanged; this pull request does not grant a new reuse license. When identifying this implementation, record the repository path and exact commit actually inspected. Use a published paper or software DOI only after a real release exists.
