"""Synthetic implementation tests only; these are not PV measurements."""
from fractions import Fraction as F
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from shortlist_transfer import evaluate, load

SYNTHETIC_CSV = "module,Source,Target\nA,100,100\nB,90,95\nC,85,90\n"
DATA = {"A": (F(100), F(100)), "B": (F(90), F(95)), "C": (F(85), F(90))}

class NominalShortlistTests(unittest.TestCase):
    def test_directional_difference(self):
        forward = evaluate(DATA, F(5))
        reverse = evaluate({k: (b, a) for k, (a, b) in DATA.items()}, F(5))
        self.assertEqual(forward["false_exclusions"], ["B"])
        self.assertEqual(forward["target_set_coverage_pct"], 50)
        self.assertEqual(reverse["false_exclusions"], [])
        self.assertEqual(reverse["excess_retentions"], ["B"])

    def test_all_half_open_boundaries(self):
        for interval in evaluate(DATA, F(5))["nominal_false_exclusion_intervals"]:
            lo, hi = F(interval["q_low_exact"]), F(interval["q_high_exact"])
            name = interval["module"]
            self.assertIn(name, evaluate(DATA, lo)["false_exclusions"])
            self.assertNotIn(name, evaluate(DATA, hi)["false_exclusions"])

    def test_exact_decimal_equality(self):
        data = {"A": (F("0.1"), F("0.2")), "B": (F("0.09"), F("0.19"))}
        self.assertEqual(evaluate(data, F("5"))["false_exclusions"], ["B"])
        self.assertEqual(evaluate(data, F("10"))["false_exclusions"], [])

    def test_positive_site_scaling(self):
        scaled = {k: (a * 7, b * 13) for k, (a, b) in DATA.items()}
        for key in ("source_shortlist", "target_shortlist", "false_exclusions", "deficits"):
            self.assertEqual(evaluate(DATA, F(5))[key], evaluate(scaled, F(5))[key])

    def test_ties_at_zero(self):
        r = evaluate({"A": (F(3), F(7)), "B": (F(3), F(7))}, F(0))
        self.assertEqual(r["source_shortlist"], ["A", "B"])
        self.assertEqual(r["false_exclusions"], [])

    def test_all_retained(self):
        self.assertEqual(evaluate(DATA, F(100))["source_shortlist"], ["A", "B", "C"])

    def test_invalid_evaluation(self):
        for data, q in (({}, F(5)), (DATA, F(-1)), ({"A": (F(0), F(1))}, F(5))):
            with self.subTest(data=data, q=q), self.assertRaises(ValueError):
                evaluate(data, q)

    def load_text(self, text, source="Source", target="Target", exclude=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text(text, encoding="utf-8")
            return load(path, source, target, exclude or set())

    def test_invalid_csv(self):
        for text in ("module,Source,Target\nA,1,2\nA,3,4\n",
                     "module,Source,Target\n,1,2\n", "module,Source\nA,1\n",
                     "module,Source,Source,Target\nA,1,2,3\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.load_text(text)

    def test_invalid_endpoints(self):
        for endpoint in ("NaN", "Inf", "", "0", "-1"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                self.load_text(f"module,Source,Target\nA,{endpoint},2\n")

    def test_identity_and_cohort_gates(self):
        for kwargs in ({"target": "Source"}, {"exclude": {"unknown"}}, {"exclude": set(DATA)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.load_text(SYNTHETIC_CSV, **kwargs)

    def test_exclusion_recomputes_maximum(self):
        reduced = self.load_text(SYNTHETIC_CSV, exclude={"A"})
        r = evaluate(reduced, F(5))
        self.assertEqual((r["source_best_endpoint"], r["target_best_endpoint"]), (90, 95))
        self.assertEqual(r["cohort_size"], 2)

    def test_command_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "synthetic.csv"
            output = root / "result.json"
            source.write_text(SYNTHETIC_CSV, encoding="utf-8")
            command = [sys.executable, str(Path(__file__).with_name("shortlist_transfer.py")),
                       "--input", str(source), "--source", "Source", "--target", "Target",
                       "--q", "5", "--output", str(output)]
            run = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(output.read_text())["false_exclusions"], ["B"])
            run = subprocess.run(command + ["--q", "NaN"], capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
