# Fresh Stage-A raw-to-result replay verification — 2026-10-18

The preserved Stage-A program was rerun from the original producer-source files available to the project. This was a **same-code reproducibility test**, not an independent new algorithm or a new scientific experiment.

The replay verified the frozen Stage-A program identity, passed six Germany/Italy/Brazil input SHA-256 gates, passed the Switzerland and Brazil archive CRC checks, reproduced the original 25/25 five-environment baseline cells, and regenerated the complete R4 extension outputs.

Four primary regenerated outputs were independently compared with the frozen R4 archive and were **byte-for-byte identical**:

- `country_source_support_gates.csv`: 230 rows
- `original_grid_27_node_site_weights.csv`: 150 rows
- `external_source_order_replay.csv`: 900 rows
- `external_pairlevel_decisions.csv`: 32,400 rows

The separate output verifier again passed **26/26** checks.

The exact digests are recorded in `qa/FRESH_RAW_TO_RESULT_REPLAY_20261018.json`.

**Boundary:** raw producer measurements are not redistributed here; a third party must reacquire them from the cited producers. This verification does not create a calibrated measurement-uncertainty budget, a new physical PV experiment, or measured laboratory-time savings.
