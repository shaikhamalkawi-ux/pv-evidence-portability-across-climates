# Project 66 — R20 bounded preference-space interpretation (derived-only)

This folder contains **new interpretation of previously archived decision records**, not new photovoltaic-module measurements or an independent prospective validation. It accompanies the author-review manuscript *Decision-Task Portability of PV Characterization Sequences: A Retrospective Cross-Climate Audit*.

## Reproduction

With Python 3.9+ and no third-party packages, from this folder run:

```bash
python run_fuzzy_interpretive_gate.py
python independent_verify_gate02.py
```

Expected: 190 historical-order records; 184 complete/correct-winner; 79 mean-improving replays; **34** campaign-proxy improvements for all positive relative weights, **30** worsenings for all such weights, **15** weight-sensitive cases with eight exact switching thresholds. The illustrative triangular profile `(0.05,1,10)` gives 34/30/15 at full support and 41/32/6 at alpha=.5. For the 11-unit Cocoa/Eugene published yields, analyst-declared q triangle `(4.5%,5%,5.5%)` allows **2–4** nominal source-to-target false exclusions; the original q=5% count is 3.

Optional (requires matplotlib):
```bash
python plot_fuzzy_gate02.py
```

Figures and source records were reviewed for the 34/30/15 full-support interpretation and Figure S3/S4 source evidence. SHA256SUMS provides the file-identity register.

## Scientific limits

- Fuzzy memberships are **illustrative preferences defined by the analyst**, not measurements of laboratory costs, expert-elicited judgments, empirical error bars, probability distributions or calibrated uncertainty.
- Same nine Stage-A products and original decision depths; no new physical I–V sweeps, climate-only causal inference, cost/time observations or prospective safe-stop claims.
- The Stage-B source is a transcription of the **11 published annual final yields** from Marion et al. (2014), DOI 10.1016/j.solener.2014.10.017; it is not a redistributed producer logger archive.
- The public 190-row decision ledger is the frozen R16/R18 derived record, SHA-256 `45060d415faa8ed84f5b1212a36893e2401913616031deddf73e244d43bb3c9d`.
- Source files are shared for inspection, not under an invented new software/data license. No publisher-owned raw measurements are redistributed.

## Interpretation

The **exact** 34/30/15 classification does not depend on a fuzzy membership function. All higher-alpha preference classifications, and possibilistic grades for shortlist exclusions, are conditional on declared fuzzy triangles; do not report them as field validation or probabilistic risk. This folder makes that separation executable rather than rhetorical.
