import copy
import json
from pathlib import Path
import unittest

from src.qgeu.validate import validate

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/qgeu/ecb-tokenized-assets-growth.qgeu.json"


class QGEUTest(unittest.TestCase):
    def load(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_reference_example_passes(self):
        self.assertEqual(validate(self.load()), [])

    def test_forecast_status_rejected(self):
        doc = self.load()
        doc["answer"]["epistemic_status"] = "FORECAST"
        self.assertTrue(validate(doc))

    def test_observed_point_requires_source(self):
        doc = self.load()
        doc["series"][0]["observations"][0]["source_ref"] = None
        self.assertTrue(validate(doc))

    def test_failed_candidate_cannot_be_selected(self):
        doc = self.load()
        doc["retrieval"]["candidates"][0]["hard_gate_pass"] = False
        self.assertTrue(validate(doc))

    def test_failed_candidate_cannot_be_scored(self):
        doc = self.load()
        doc["retrieval"]["candidates"][0]["hard_gate_pass"] = False
        doc["retrieval"]["candidates"][0]["score"] = 99
        self.assertTrue(validate(doc))

    def test_two_points_line_chart_rejected(self):
        doc = self.load()
        doc["graph"]["chart_type"] = "line"
        self.assertTrue(validate(doc))

    def test_scalar_arithmetic_must_reproduce(self):
        doc = self.load()
        doc["derivation"]["scalar_outputs"]["ratio"] = 10
        self.assertTrue(validate(doc))

    def test_causal_intent_routes_out(self):
        doc = self.load()
        doc["question"]["causal_intent"] = True
        self.assertTrue(validate(doc))


if __name__ == "__main__":
    unittest.main()
