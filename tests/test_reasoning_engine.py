"""
Unit Tests for Multi-Metric Reasoning Engine.
"""

import unittest
from core.reasoning_engine import ReasoningEngine

class TestReasoningEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ReasoningEngine()

    def test_hackathon_benchmark_use_case(self):
        """
        Verify the exact benchmark use case from the hackathon document:
        Input:
          - Soil organic carbon: 0.3%
          - Rainfall: low
          - Crop: monoculture wheat
          - Region: semi-arid
        Expected:
          - Multi-metric handling of >= 3 variables
          - Agroforestry / intercropping recommendation
          - Quantitative soil carbon and biodiversity estimates
          - Credible citations (FAO, IPCC)
        """
        input_state = {
            "soil_organic_carbon": 0.3,
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid"
        }

        output = self.engine.analyze_ecosystem(input_state)

        # 1. Multi-metric variable handling (>= 3 variables)
        self.assertGreaterEqual(output["variable_count"], 3, "Must evaluate at least 3 variables simultaneously.")
        
        # 2. Causal interaction nexus
        nexus = output["multi_metric_nexus"]
        self.assertIn("interaction_chains", nexus)
        self.assertGreater(len(nexus["interaction_chains"]), 0)

        # 3. Recommendations check
        recs = output["recommendations"]
        self.assertGreater(len(recs), 0, "Must provide actionable recommendations.")

        rec_titles = [r["title"] for r in recs]
        has_agroforestry = any("Agroforestry" in t or "Intercropping" in t for t in rec_titles)
        self.assertTrue(has_agroforestry, "Must suggest agroforestry / intercropping as mandated in document.")

        # 4. Check quantitative impacts and citations on primary recommendation
        primary_rec = recs[0]
        self.assertIn("multi_metric_impacts", primary_rec)
        self.assertGreaterEqual(len(primary_rec["multi_metric_impacts"]), 2)

        citations_str = " ".join(primary_rec["citations"])
        self.assertTrue("FAO" in citations_str, "Must cite Food and Agriculture Organization (FAO).")
        self.assertTrue("IPCC" in citations_str, "Must cite Intergovernmental Panel on Climate Change (IPCC).")

    def test_spatial_context_enrichment(self):
        """Test that geo-coordinates enrich missing baseline metrics."""
        state_with_coords = {
            "coordinates": {"lat": 26.2, "lon": 73.0}, # Thar desert margin / semi-arid
            "crop": "pearl millet"
        }
        output = self.engine.analyze_ecosystem(state_with_coords)
        env_state = output["environmental_state"]
        self.assertIn("spatial_context", env_state)
        self.assertIsNotNone(env_state.get("rainfall_mm") or env_state.get("rainfall_category"))

if __name__ == "__main__":
    unittest.main()
