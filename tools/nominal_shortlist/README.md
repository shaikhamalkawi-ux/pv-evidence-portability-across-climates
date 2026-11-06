# Nominal shortlist-transfer diagnostic

A standard-library-only implementation of the existing shortlist definitions in the Project 66 photovoltaic evidence-portability study. This directory is a code-review addition, not a new empirical result, tagged software release, or journal publication.

## Input and scientific scope

Supply a UTF-8 CSV with a `module` identifier column and two distinct, named, strictly positive endpoint columns. Every retained identifier must refer to the scientifically comparable candidate intended by the study. The program cannot establish physical identity, comparable units, representative periods, or measurement quality.

For candidate i and site c, the percentage deficit is `100 * (1 - Y[i,c] / max(Y[:,c]))`, computed within the declared cohort. At nonnegative cutoff q, retain candidates with deficit <= q. A nominal source-to-target false exclusion is a target-retained candidate missing from the source set. Each directional exclusion interval includes its lower endpoint and excludes its upper endpoint. Fraction arithmetic preserves equality for supplied decimal values; it does not remove input rounding or measurement uncertainty.

## Run

From this directory, with Python 3.10 or later:

```bash
python -m unittest -v test_shortlist test_input_safety
python shortlist_transfer.py --input own_comparable_endpoints.csv --source Source --target Target --q 5 --output result.json
```

Repeat the calculation with source and target exchanged. Use `--exclude ID` only for a scientifically justified cohort restriction. Exclusion recomputes the cohort maximum; a changed exclusion count is not an improvement of the method.

## Input and output safeguards

CSV quoting must be valid and each nonempty record must have the declared number of fields. Header names must be nonempty, unique, and unpadded. Extra named columns are allowed when their fields are present. The `module` column cannot also be used as an endpoint.

The output must not be the input path, a filesystem alias of it, or a symbolic link. A successful run replaces an existing ordinary result file at the explicitly selected output path. The result is serialized before writing and a temporary file in the destination directory is atomically replaced into place; failed validation or a failed replacement preserves an existing result. Invalid text encoding, CSV syntax, and numbers that cannot be represented in the JSON display fields produce a controlled error. These checks assume a normal local filesystem without adversarial concurrent path replacement; they are not a filesystem security boundary.

## Code-review history and tests

The R13 calculator copied the R11 implementation, SHA-256 `d101f556f4e048f394e1a39ed1c45862517b55a3f0e0a44ba2b893a47bfbf257`. R14 corrects input/output handling: malformed row lengths are rejected and the input cannot be overwritten by selecting it as output. The mathematical `evaluate()` function is byte-identical to R13. R14 is no longer byte-identical as a complete script.

The suite contains 29 tests: the original 12 semantic/CLI tests plus 17 input/output safety tests. All fixtures are synthetic implementation checks, not measured PV data. Symlink or hardlink tests can be skipped on filesystems that do not support those features; report the executed/skipped counts for the environment actually used. No cross-platform certification is claimed.

## Interpretation and rights

Outputs are deterministic comparisons of supplied point estimates. They are not uncertainty-calibrated screening certificates, procurement recommendations, causal climate estimates, or optimal measurement schedules. This is Stage B code only, not reproduction of Stage A or the entire manuscript.

No measured producer table, laboratory workbook, frozen weather weights, or private manuscript is included here. No journal DOI, acceptance, new license grant, or software DOI is asserted. Existing repository and third-party rights are unchanged. Identify the implementation by the exact repository path and commit inspected; cite a published paper or DOI only when a real record exists.
