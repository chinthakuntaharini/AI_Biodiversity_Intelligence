"""
Spatial Context and Geo-Coordinate Resolver.
Maps geographical coordinates (latitude/longitude) to biomes, Köppen climate classes,
native vegetation profiles, and baseline environmental indicators.
"""

import os
import json
from typing import Dict, Any, Optional, Tuple

class SpatialResolver:
    def __init__(self, data_file: Optional[str] = None):
        if data_file is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file = os.path.join(base_path, "data", "spatial_biomes.json")
        
        self.data_file = data_file
        self.biomes: list[Dict[str, Any]] = []
        self._load_biomes()

    def _load_biomes(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.biomes = json.load(f)

    def resolve(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Resolves latitude and longitude to an ecoregion profile.
        Checks bounding polygons first, then falls back to latitude band heuristic.
        """
        # Check explicit bounding boxes
        for biome in self.biomes:
            for bbox in biome.get("bounding_boxes", []):
                if (bbox["lat_min"] <= lat <= bbox["lat_max"] and
                    bbox["lon_min"] <= lon <= bbox["lon_max"]):
                    return {
                        "matched_by": "geographic_bounding_box",
                        "zone_name": bbox["name"],
                        "biome_id": biome["id"],
                        "biome_name": biome["name"],
                        "koppen_classes": biome["koppen_classes"],
                        "baseline_metrics": biome["baseline_metrics"]
                    }

        # Fallback heuristic based on latitude and regional zones
        abs_lat = abs(lat)
        if abs_lat <= 23.5:
            # Tropical / Subtropical
            default_biome = next((b for b in self.biomes if b["id"] == "BIOME-TROP-DRY"), self.biomes[0])
            matched_name = "Tropical Dry Zone"
        elif 23.5 < abs_lat <= 38.0:
            # Semi-arid / Mediterranean belt
            default_biome = next((b for b in self.biomes if b["id"] == "BIOME-SEMIARID"), self.biomes[0])
            matched_name = "Subtropical / Semi-Arid Belt"
        else:
            # Temperate zone
            default_biome = next((b for b in self.biomes if b["id"] == "BIOME-TEMPERATE"), self.biomes[0])
            matched_name = "Temperate Continental / Maritime Belt"

        return {
            "matched_by": "latitude_biome_classification",
            "zone_name": matched_name,
            "biome_id": default_biome["id"],
            "biome_name": default_biome["name"],
            "koppen_classes": default_biome["koppen_classes"],
            "baseline_metrics": default_biome["baseline_metrics"]
        }

    def enrich_ecosystem_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        If coordinates are provided, enriches missing metrics from spatial baselines.
        """
        coords = state.get("coordinates")
        if not coords or not isinstance(coords, dict):
            return state

        lat = coords.get("lat") or coords.get("latitude")
        lon = coords.get("lon") or coords.get("longitude")

        if lat is not None and lon is not None:
            spatial_info = self.resolve(float(lat), float(lon))
            state["spatial_context"] = spatial_info

            baselines = spatial_info["baseline_metrics"]
            if not state.get("rainfall_category") and not state.get("rainfall_mm"):
                rainfall_range = baselines.get("annual_rainfall_range_mm", [400, 800])
                avg_rain = sum(rainfall_range) / len(rainfall_range)
                state["rainfall_mm"] = avg_rain
                state["rainfall_category"] = "low" if avg_rain < 500 else ("medium" if avg_rain < 900 else "high")

            if not state.get("region"):
                state["region"] = spatial_info["biome_name"]

            if not state.get("soil_type") and baselines.get("dominant_soil_types"):
                state["soil_type"] = baselines["dominant_soil_types"][0]

        return state
