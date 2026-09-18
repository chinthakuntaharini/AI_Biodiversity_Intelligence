"""
Integration Tests for FastAPI REST Endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertGreater(data["indexed_documents"], 0)

    def test_chat_turn_endpoint(self):
        payload = {
            "message": "Soil organic carbon: 0.3%, Rainfall: low, Crop: monoculture wheat, Region: semi-arid"
        }
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_complete"])
        self.assertIsNotNone(data["analysis"])

    def test_analyze_structured_endpoint(self):
        payload = {
            "soil_organic_carbon": 0.3,
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid"
        }
        response = self.client.post("/api/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("recommendations", data)
        self.assertGreater(len(data["recommendations"]), 0)

    def test_spatial_lookup_endpoint(self):
        payload = {"latitude": 26.28, "longitude": 73.02}
        response = self.client.post("/api/spatial/lookup", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("biome_name", data)

    def test_knowledge_query_endpoint(self):
        payload = {"query": "agroforestry Faidherbia", "top_k": 2}
        response = self.client.post("/api/knowledge/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["results_count"], 0)

if __name__ == "__main__":
    unittest.main()
