#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "directional_transfer_5site.py": "79ec83a814a0f665c310d75de42c40471e9491f4ca09f1d54f1ad26b5b8eddc9",
    "reproduce_characterization_depth.py": "bf1fa4e7d7c8784b0f140ef4f55a412e1a04857409058479ed0585b290fafdff",
    "verify_r12.py": "26d6cbb6822de3b557bbfd4905510316ee035656dae3028488f537313cac2c7e",
    "SWITZERLAND_REQUIRED_FILES.csv": "9db4ca92fd426be89794701765042958c182a3971f7c23c806d30fd15ef9b522",
    "environment.txt": "d72cf2456e41f5e26828f10974fbd222b88a867e8dad946315f806056779d994",
}
failed = []
for name, expected in EXPECTED.items():
    p = ROOT / name
    actual = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
    ok = actual == expected
    print(("PASS" if ok else "FAIL"), name, actual)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit("Source-integrity failure: " + ", ".join(failed))
print(f"{len(EXPECTED)}/{len(EXPECTED)} public Stage-A source-integrity checks PASS")
