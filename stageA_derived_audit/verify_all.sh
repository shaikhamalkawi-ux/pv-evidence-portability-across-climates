#!/usr/bin/env bash
set -euo pipefail
: "${1:?Usage: bash verify_all.sh /absolute/path/to/Project62_R4_Multicountry_Reproducibility.zip}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/verification_output"
cp "$ROOT/results/primary_source_workload.csv" "$ROOT/verification_output/primary_source_workload.csv"
python "$ROOT/reproduce/engineering_cost_audit.py" "$1" "$ROOT/verification_output"
python "$ROOT/reproduce/verify_independent.py" "$1" "$ROOT/verification_output/vectorized.json"
python "$ROOT/reproduce/verify_shadow_mode.py" "$1" --output-dir "$ROOT/verification_output/shadow_mode"
echo 'ALL DERIVED REPLAY GATES PASS'
