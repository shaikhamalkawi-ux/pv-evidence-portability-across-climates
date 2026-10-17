#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_external_outputs_independent.py
printf '
DERIVED ORIGINAL OUTPUT QA PASS (26 CHECKS). New Stage-A 188/188 + 5400/5400 audits require the exact original SHA-locked R4 archive.
'
