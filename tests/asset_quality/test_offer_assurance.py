from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.asset_quality.domain import OfferAsset, ValueEquationRule
from src.asset_quality.validate import validate_tree


class OfferAssuranceTests(unittest.TestCase):
    def test_unmeasured_client_effort_is_warning_not_false_precision(self):
        payload = {
            "asset_id": "programme.example",
            "asset_kind": "programme",
            "source_path": "page.html",
            "canonical_url": "https://mickael-umt.com/programme/example/",
            "value_equation": {
                "dream_outcome": {"statement": "A bounded result", "evidence_refs": ["proof.json"]},
                "perceived_likelihood": {"evidence_unit_count": 1, "evidence_coverage": 0.8, "evidence_refs": ["proof.json"]},
                "time_delay": {"full_outcome": "4 weeks", "first_verified_value": "week 1", "measurement_status": "planned"},
                "effort_sacrifice": {"client_inputs": ["Sponsor"], "estimated_commitment": None, "measurement_status": "to_measure"},
                "risk_reversal": {"guarantee_type": "deliverable-bound", "controlled_commitments": ["Deliver report"], "excluded_outcomes": ["Regulatory compliance is not guaranteed."]},
            },
            "quality_targets": {"evidence_coverage_min": 0.5},
            "mesh": {"programme_ids": [], "learning_program_ids": [], "capability_ids": [], "app_tool_ids": [], "mesh_status": "partial"},
        }
        findings = ValueEquationRule().validate(OfferAsset.from_mapping(payload))
        self.assertIn("AQ-VAL-010", {finding.code for finding in findings})
        self.assertNotIn("error", {finding.severity for finding in findings if finding.code == "AQ-VAL-010"})

    def test_duplicate_primary_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quality" / "assets").mkdir(parents=True)
            (root / "page.html").write_text("ok", encoding="utf-8")
            base = {
                "schema_version": "1.0",
                "asset_id": "programme.example",
                "asset_kind": "programme",
                "source_path": "page.html",
                "canonical_url": "https://mickael-umt.com/programme/example/",
                "value_equation": {
                    "dream_outcome": {"statement": "Outcome", "evidence_refs": ["proof"]},
                    "perceived_likelihood": {"evidence_unit_count": 1, "evidence_coverage": 1.0, "evidence_refs": ["proof"]},
                    "time_delay": {"full_outcome": "1 week", "first_verified_value": "day 1", "measurement_status": "planned"},
                    "effort_sacrifice": {"client_inputs": ["Sponsor"], "estimated_commitment": "1 hour", "measurement_status": "planned"},
                    "risk_reversal": {"guarantee_type": "none", "controlled_commitments": [], "excluded_outcomes": []},
                },
                "quality_targets": {"evidence_coverage_min": 0.5, "unsupported_claims_max": 0, "first_verified_value_declared": True},
                "mesh": {"programme_ids": [], "learning_program_ids": [], "capability_ids": [], "app_tool_ids": [], "mesh_status": "partial"},
            }
            for name in ("a.json", "b.json"):
                (root / "quality" / "assets" / name).write_text(json.dumps(base), encoding="utf-8")
            report = validate_tree(root=root, manifests_dir=root / "quality" / "assets")
            self.assertEqual("FAIL", report["status"])
            self.assertTrue(any(f["code"] == "AQ-ID-006" for asset in report["assets"] for f in asset["findings"]))


if __name__ == "__main__":
    unittest.main()
