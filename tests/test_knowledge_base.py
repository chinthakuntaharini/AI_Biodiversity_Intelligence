"""
Unit Tests for Knowledge Base and Retrieval Engine.
"""

import unittest
from core.knowledge_base import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()

    def test_corpus_loading(self):
        """Ensure documents across all 5 core domains are loaded."""
        self.assertGreater(len(self.kb.documents), 0, "Corpus should contain indexed documents.")
        domains = self.kb.get_all_domains()
        expected_domains = ["soil_health", "land_cover", "biodiversity_indicators", "climate_factors", "human_impact"]
        for exp in expected_domains:
            self.assertIn(exp, domains, f"Missing expected domain: {exp}")

    def test_retrieval_query(self):
        """Test that query for soil organic carbon returns relevant chunks and citations."""
        results = self.kb.retrieve("soil organic carbon legume cover crops", top_k=2)
        self.assertGreater(len(results), 0, "Retrieval should return results.")
        top_res = results[0]
        self.assertIn("citations", top_res)
        self.assertGreater(len(top_res["citations"]), 0, "Top result should have citations.")
        citations_str = " ".join(top_res["citations"])
        self.assertTrue("FAO" in citations_str or "IPCC" in citations_str, "Should cite FAO or IPCC.")

    def test_domain_filtering(self):
        """Test domain-filtered retrieval."""
        results = self.kb.retrieve("pollinators", domain="biodiversity_indicators", top_k=2)
        for r in results:
            self.assertEqual(r["domain"], "biodiversity_indicators")

if __name__ == "__main__":
    unittest.main()
