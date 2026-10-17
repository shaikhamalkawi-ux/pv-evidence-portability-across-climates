#!/bin/sh
set -eu
bash verify_derived_only.sh
python stageB_derived_audit/reproduce/verify_shortlists.py
