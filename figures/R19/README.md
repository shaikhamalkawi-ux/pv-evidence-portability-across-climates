# Task-conditioned portability figure — display-only enhancement

The PDF shows (a) all 184 correctness-gated complete runs and (b) a magnified window of the same observations near zero pairwise mean change. Filled points are non-reversals; open circles mark the 12 strict task reversals. No jitter, interpolation, resampling, independent experimental units, or statistical confidence is implied.

To recreate:

```bash
pip install -r figures/R19/requirements.txt
python figures/R19/plot_task_reversal_R19.py \
  reproducibility/R18/R16_FROZEN_R15_TASK_COMPARISONS_PRIMARY38.csv \
  task_portability_reversal_map_with_inset.pdf
```

The script explicitly asserts the frozen input SHA-256 and the 184/12 denominators. Figure aesthetics differ from the earlier single-panel rendering; source coordinates and classifications are unaltered.
