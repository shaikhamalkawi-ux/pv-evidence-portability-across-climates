#!/bin/sh
set -eu
python code/stageA_original/verify_source_hashes.py
bash verify_derived_only.sh
python stageB_derived_audit/reproduce/verify_shortlists.py
