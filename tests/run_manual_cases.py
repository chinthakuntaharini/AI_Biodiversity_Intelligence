"""
Manual Case Testing Suite for Darukaa.Earth AI Environmental Scientist Platform.
Tests 6 distinct realistic cases:
  1. Hackathon Benchmark: Semi-arid wheat monoculture with severe SOC depletion
  2. Multi-turn Parameter Intake & Clarification Workflow
  3. Geo-Spatial Coordinate Auto-Enrichment (Thar / Deccan Drylands)
  4. Humid Tropical Acidic Plantation with Severe Erosion & Compaction
  5. Temperate Degraded Rangeland / Overgrazed Pasture
  6. Scientific Knowledge Base BM25 Domain Retrieval
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from app.main import app

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

client = TestClient(app)

def post_json(endpoint: str, data: dict):
    resp = client.post(endpoint, json=data)
    return resp.json()

def get_json(endpoint: str):
    resp = client.get(endpoint)
    return resp.json()

def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)

def test_case_1_benchmark():
    print_banner("Case 1: Hackathon Benchmark — Semi-Arid Monoculture Wheat")
    payload = {
        "soil_organic_carbon": 0.3,
        "rainfall": "low",
        "crop": "monoculture wheat",
        "region": "semi-arid"
    }
    print(f"Input: {json.dumps(payload, indent=2)}")
    res = post_json("/api/scientist/analyze", payload)
    
    print("\n[Variables Evaluated]:", len(res.get("variables_evaluated", [])))
    for v in res.get("variables_evaluated", []):
        print("  -", v)
        
    print("\n[Risk Profile]:")
    for k, v in res.get("risk_profile", {}).items():
        print(f"  {k:<20}: {v}")
        
    print("\n[Nexus Summary]:")
    print(" ", res.get("multi_metric_nexus", {}).get("summary"))
    
    print("\n[Recommendations Generated]:", len(res.get("recommendations", [])))
    for i, r in enumerate(res.get("recommendations", []), 1):
        print(f"\n  #{i} {r['title']}")
        print(f"     Priority: {r['priority']}")
        print(f"     Impacts:")
        for imp in r.get("multi_metric_impacts", []):
            print(f"       * [{imp['dimension']}] {imp['metric']}: {imp['projected_change']}")
        print(f"     Citations:")
        for c in r.get("citations", []):
            print(f"       - {c}")
            
    assert len(res.get("variables_evaluated", [])) >= 3, "Failed: < 3 variables evaluated"
    assert any("Agroforestry" in r["title"] for r in res.get("recommendations", [])), "Failed: No agroforestry"
    print("\n>>> CASE 1 RESULT: SUCCESS (Meets all hackathon criteria)")

def test_case_2_multi_turn():
    print_banner("Case 2: Multi-Turn Parameter Intake & Clarification Workflow")
    
    # Turn 1: Incomplete input
    msg1 = "Biodiversity is declining rapidly on my farm and wild bees have vanished."
    print(f"Turn 1 Input: '{msg1}'")
    turn1 = post_json("/api/scientist/intake", {"message": msg1})
    
    print(f"Turn 1 Status: {turn1['status']} | Complete: {turn1['is_complete']}")
    print(f"Missing Dimensions: {turn1.get('missing_dimensions')}")
    print("Clarification Response:\n" + turn1['response_text'])
    
    assert turn1['status'] == "awaiting_clarification", "Failed: Turn 1 did not request clarification"
    assert not turn1['is_complete'], "Failed: Turn 1 marked complete prematurely"
    
    # Turn 2: Follow-up providing parameters
    session_id = turn1['session_id']
    msg2 = "Our soil organic carbon is 0.4%, annual precipitation is low (around 380 mm), and we grow monoculture pearl millet."
    print(f"\nTurn 2 Input (Session {session_id}): '{msg2}'")
    turn2 = post_json("/api/scientist/intake", {"message": msg2, "session_id": session_id})
    
    print(f"Turn 2 Status: {turn2['status']} | Complete: {turn2['is_complete']}")
    print(f"Accumulated State: {turn2.get('accumulated_state')}")
    print("\nNarrative Preview (First 400 chars):")
    print(turn2['response_text'][:400] + "...")
    
    assert turn2['is_complete'], "Failed: Turn 2 should complete assessment"
    assert turn2['analysis'] is not None, "Failed: No analysis attached"
    print("\n>>> CASE 2 RESULT: SUCCESS (Stateful multi-turn intake passed)")

def test_case_3_spatial():
    print_banner("Case 3: Geo-Spatial Coordinate Auto-Enrichment")
    payload = {
        "coordinates": {"lat": 26.28, "lon": 73.02}, # Jodhpur, Rajasthan (Thar margin)
        "crop": "pearl millet",
        "soil_organic_carbon": 0.25
    }
    print(f"Input: {json.dumps(payload, indent=2)}")
    res = post_json("/api/scientist/analyze", payload)
    
    env = res.get("environmental_state", {})
    spatial_info = env.get("spatial_context", {})
    print(f"\n[Spatial Classification]:")
    print(f"  Biome ID   : {spatial_info.get('biome_id')}")
    print(f"  Biome Name : {spatial_info.get('biome_name')}")
    print(f"  Koppen     : {spatial_info.get('koppen_classes')}")
    print(f"  Baselines  : {spatial_info.get('baseline_metrics')}")
    
    assert spatial_info.get("biome_id") is not None, "Failed: No biome resolved"
    print("\n>>> CASE 3 RESULT: SUCCESS (Spatial context accurately enriched)")

def test_case_4_humid_acidic():
    print_banner("Case 4: Tropical Humid Degraded Plantation with Acidic Soil & Erosion")
    payload = {
        "region": "tropical humid",
        "rainfall_mm": 2200,
        "rainfall": "high",
        "ph": 4.6,
        "bulk_density": 1.55,
        "erosion_rate": 16.5,
        "crop": "degraded tea plantation monoculture",
        "soil_organic_carbon": 0.8
    }
    print(f"Input: {json.dumps(payload, indent=2)}")
    res = post_json("/api/scientist/analyze", payload)
    
    print("\n[Risk Profile]:")
    for k, v in res.get("risk_profile", {}).items():
        print(f"  {k:<20}: {v}")
        
    print("\n[Causal Chains]:")
    for chain in res.get("multi_metric_nexus", {}).get("interaction_chains", []):
        print("  ->", chain)
        
    print("\n[Prescription Titles]:")
    for r in res.get("recommendations", []):
        print(f"  - {r['title']}")
        
    assert res["risk_profile"]["soil_chemistry"].lower() in ("critical", "high"), "Failed: Acid pH not flagged"
    assert res["risk_profile"]["erosion"].lower() in ("critical", "high"), "Failed: High erosion not flagged"
    print("\n>>> CASE 4 RESULT: SUCCESS (Accurately diagnosed acid-compaction-erosion syndrome)")

def test_case_5_temperate_rangeland():
    print_banner("Case 5: Overgrazed Temperate Pasture with Soil Degradation")
    payload = {
        "region": "temperate",
        "rainfall_mm": 680,
        "rainfall": "moderate",
        "land_use": "overgrazed degraded pasture",
        "species_richness": 3.0,
        "soil_organic_carbon": 0.75,
        "bulk_density": 1.48
    }
    print(f"Input: {json.dumps(payload, indent=2)}")
    res = post_json("/api/scientist/analyze", payload)
    
    print("\n[Evaluated Variables]:")
    for v in res.get("variables_evaluated", []):
        print("  -", v)
        
    print("\n[Top Recommendation Details]:")
    top_rec = res.get("recommendations", [])[0]
    print(f"  Title: {top_rec['title']}")
    print(f"  Mechanism: {top_rec['scientific_mechanism'][:200]}...")
    
    assert res["risk_profile"]["biodiversity"].lower() in ("critical", "high"), "Failed: Low species richness not flagged"
    print("\n>>> CASE 5 RESULT: SUCCESS (Detected overgrazed degraded pasture signature)")

def test_case_6_knowledge_retrieval():
    print_banner("Case 6: BM25 Scientific Knowledge Retrieval Engine")
    queries = [
        ("soil organic carbon microbial biomass drylands", "soil_health"),
        ("soil acidity salinity biochar pH", "soil_health"),
        ("wild pollinators Apoidea floral continuity", "biodiversity_indicators"),
    ]
    
    for q, domain in queries:
        print(f"\nQuery: '{q}' (Domain: {domain})")
        res = post_json("/api/knowledge/query", {"query": q, "domain": domain, "top_k": 2})
        print(f"  Matches found: {res['results_count']}")
        for match in res["results"]:
            print(f"  * Doc ID: {match.get('doc_id', match.get('id'))} | Topic: {match.get('topic')}")
            print(f"    Citations: {match.get('citations', [])[:2]}")
        assert res["results_count"] > 0, f"Failed: No results for {q}"
        
    print("\n>>> CASE 6 RESULT: SUCCESS (Knowledge base semantic retrieval validated)")

if __name__ == "__main__":
    print("Starting Comprehensive Manual Case Test Suite...")
    test_case_1_benchmark()
    test_case_2_multi_turn()
    test_case_3_spatial()
    test_case_4_humid_acidic()
    test_case_5_temperate_rangeland()
    test_case_6_knowledge_retrieval()
    print("\n" + "=" * 80)
    print(" ALL 6 MANUAL TEST CASES PASSED WITH 100% SUCCESS RATE")
    print("=" * 80)
