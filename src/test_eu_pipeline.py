import unittest

from eu_pipeline import anchor_variants, atomic_gate, extract_numeric_anchors, normalize_text, xpath_check


class EvidenceGateUnitTests(unittest.TestCase):
    def test_numeric_anchor_normalization(self):
        anchors = extract_numeric_anchors("Across 4,867 developers, tasks increased 26.08% (SE 10.3%).")
        self.assertIn("4867", anchors)
        self.assertIn("26.08%", anchors)
        self.assertIn("10.3%", anchors)

    def test_percent_normalization(self):
        self.assertIn("26.08 percent", anchor_variants("26.08%"))
        self.assertEqual("68 percent to 30 percent", normalize_text("68% to 30%"))

    def test_atomic_gate_accepts_complete_eu(self):
        ok, missing = atomic_gate({
            "quant_variable": "adoption change",
            "quant_value": "-38",
            "quant_unit": "percentage points",
            "population": "1,138 ED patients",
            "period": "4 weeks",
            "primary_source_url": "https://example.org/paper",
        })
        self.assertTrue(ok)
        self.assertEqual([], missing)

    def test_atomic_gate_rejects_non_numeric_value(self):
        ok, missing = atomic_gate({
            "quant_variable": "effect",
            "quant_value": "large",
            "quant_unit": "percentage points",
            "population": "sample",
            "period": "2026",
            "primary_source_url": "https://example.org/paper",
        })
        self.assertFalse(ok)
        self.assertIn("quant_value:not_numeric", missing)

    def test_xpath_must_match_exactly_once(self):
        body = "<html><body><main><section data-section-id='intent'><h3 class='scene-card-headline'>A</h3></section></main></body></html>"
        result = xpath_check(body, "//section[@data-section-id='intent']//h3")
        self.assertTrue(result.ok)
        self.assertEqual(1, result.count)

    def test_xpath_multiple_match_fails(self):
        body = "<html><body><p>A</p><p>B</p></body></html>"
        result = xpath_check(body, "//p")
        self.assertFalse(result.ok)
        self.assertEqual(2, result.count)


if __name__ == "__main__":
    unittest.main()
