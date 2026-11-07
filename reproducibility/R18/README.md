# R18 — Validity-gated task-reversal certificate (derived records only)

These files reproduce the frozen-ledger classifications underlying the research manuscript **Decision-Task Portability of PV Characterization Sequences: A Retrospective Cross-Climate Audit**.

## Run

Requires Python 3.9+ (standard library). No original producer measurements are included.

```bash
cd reproducibility/R18
python verify_R16_validity_gate.py
python derive_R18_magnitude_audit.py
```

Expected: 190 historical-order runs; 188 complete all-pairs records; 184 correct-winner and complete records; 16 apparent sign reversals, 4 with an incorrect accepted winner; 12 validity-gated strict task reversals. These 12 runs concern 11 distinct target records, with 9 Brazil, 2 Germany, and 1 Italy run-level cases. All 12 have <5% absolute change in pairwise mean depth, and 9 change accepted-winner depth by one cell. There are 21 of 79 mean-improving runs that worsen both campaign proxies in the frozen study.

**Scope:** Retrospective dependent replays. The public ledgers are *derived decision records*, not original IEC/PV I–V curves or new physically independent replications. Full raw-to-derived reproduction still requires third-party producer data (see repository's `THIRD_PARTY_DATA.md`). Avoid interpreting the row counts as statistical sample sizes or lab-time savings.

## Auditable sources

- `R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv`: exact frozen 190-row metric ledger.
- `R16_COMPLETE_VALIDITY_GATED_CENSUS.csv`: full 190-row classification.
- `R18_VALIDITY_GATED_12_CASE_MAGNITUDES.csv`: exact 12-case magnitude table.
- `verify_R16_validity_gate.py`: independent classification checks.
- `derive_R18_magnitude_audit.py`: regenerates 12-case table and QA.
- `R18_MAGNITUDE_QA.json`: declared expected hashes/denominators.

These materials may be read without downloading the original third-party raw measurements. New figure-generation code in `figures/R19` uses exactly the frozen 190-row CSV with SHA-256 gate. The R19 display change is graphical only, not a new scientific result.
