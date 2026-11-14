# Project 66 — R21 graph-bottleneck interpretation of task reversal

This folder contains a **derived-only, deterministic** graph attribution of the R15/R20 photovoltaic characterization-order replay. It explains why the pair-average stopping burden can worsen while correct-winner identification becomes earlier, or vice versa. The original nine-product response panel, measured source data, 27 conditions, and accepted pairwise decisions were **not changed**. Do not treat the 38 target histories or 12 reversal rows as independent experiments.

## Reproduce (Python 3, NumPy, pandas, Matplotlib)

```bash
python audit_graph.py
python independent_graph_verify.py
python audit_pareto.py
python verify_pareto_integer.py
python plot_graph_publication.py
sha256sum -c SHA256_INPUTS.txt
```

Expected original SHA-256 of the three frozen inputs is checked by `independent_graph_verify.py` and `verify_pareto_integer.py`. `SHA256_INPUTS.txt` is a separate source identity register. The plot is **display-only**, with embedded TrueType (Type-42) fonts; it does not move or jitter data points.

## Primary explanatory findings

- 32,400 archived pair-decision rows, 900 target/order groups; 38 prespecified external target distributions, 5 historical orders each.
- 188/190 historical order runs are all-pairs-complete; 184 are both complete and correct-winner.
- Twelve valid strict reversals: nine pair-mean-worse/winner-earlier, three pair-mean-better/winner-later.
- In the former nine, non-winner-edge depth sums increase in all nine and winner-star depth sums do not increase in any; the latter three all reduce non-winner-edge totals.
- Example Trieste under Cocoa: winner-star sum -9, other-edge sum +23, pair-mean +14/36; accepted correct winner 14 to 8, Kall 14 to 17.
- Example Brazil PS_006 under Albuquerque: star sum -1, other sum -3, pair-mean -4/36 while the **maximum** winner-star comparison rises 9 to 11.
- For Pareto interpretation of the fixed tested orders only: 222 eligible target/order records, 74 nondominated, 23/38 targets with multiple nondominated options, and 16 target-local heuristics dominated within the tested set.

## Source and rights boundaries

`external_pairlevel_decisions.csv`, `R15_TASK_METRICS_PRIMARY38.csv`, and `R15_TASK_COMPARISONS_PRIMARY38.csv` are archived **derived** records, not original raw I-V measurements or weather logger files. Third-party raw data are not redistributed here. Original provider source identifiers and any source terms must be respected. The mathematical identities are elementary graph identities, not claimed as new graph-theory theorems. No externally validated stopping rule, calibrated measurement risk, causal climate attribution, measured lab-time saving, cost ratio, or prospective order recommendation is claimed.

`Graph_12ValidReversals.csv`, `Graph_Complete188.csv`, `Pareto_EligibleOrder_Census.csv`, the checks and `Figure_Graph12_StarVsOther.pdf` are derived from the above inputs. Code and derived files are publicly inspectable; no permissive license is asserted by this package.
