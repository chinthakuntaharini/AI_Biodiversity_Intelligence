"""
Scientific Session Manager — Multi-Turn Ecological Assessment Workflow.

Manages multi-turn environmental data collection sessions, functioning
as a field ecologist's intake protocol rather than a chat dialogue.
Extracts environmental parameters from natural language, validates
completeness for rigorous multi-metric analysis, and maintains
stateful parameter accumulation across conversation turns.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from .reasoning_engine import ReasoningEngine


class EcologicalSession:
    """
    Stateful environmental parameter accumulation session.
    Represents an ongoing field assessment with accumulated data.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.accumulated_state: Dict[str, Any] = {}
        self.last_analysis: Optional[Dict[str, Any]] = None
        self.turn_count: int = 0

    def add_exchange(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if role == "user":
            self.turn_count += 1

    def update_state(self, new_vars: Dict[str, Any]):
        """Merge new environmental parameters into accumulated state."""
        for key, value in new_vars.items():
            if value is not None and value != "":
                self.accumulated_state[key] = value

    def get_state_summary(self) -> str:
        s = self.accumulated_state
        parts = []
        if s.get("soil_organic_carbon"):
            parts.append(f"SOC: {s['soil_organic_carbon']}%")
        if s.get("rainfall") or s.get("rainfall_mm"):
            parts.append(f"Rainfall: {s.get('rainfall_mm', s.get('rainfall', 'N/A'))}")
        if s.get("crop") or s.get("land_use"):
            parts.append(f"Land: {s.get('crop', s.get('land_use', 'N/A'))}")
        if s.get("region"):
            parts.append(f"Region: {s['region']}")
        if s.get("ph"):
            parts.append(f"pH: {s['ph']}")
        return " | ".join(parts) if parts else "No parameters yet"


class ScientificSessionManager:
    """
    Multi-turn ecological parameter intake manager.

    Behaves as a field ecologist conducting a structured site assessment.
    Systematically collects environmental data, flags missing critical
    parameters, and triggers full scientific analysis when sufficient
    data is available.
    """

    # Minimum parameters required for rigorous analysis
    REQUIRED_DIMENSIONS = {
        "soil": ["soil_organic_carbon", "soc", "soil_type", "ph"],
        "hydrology": ["rainfall", "rainfall_mm", "rainfall_pattern"],
        "vegetation": ["crop", "current_crop", "land_use", "land_cover"],
    }

    # Scientific intake questions for missing parameters
    INTAKE_QUESTIONS = {
        "soil": (
            "Soil health parameters are required for complete diagnosis. "
            "Please provide: Soil Organic Carbon % (e.g., SOC: 0.3%), "
            "soil pH, or general soil condition (e.g., 'degraded', 'compacted', 'sandy loam')."
        ),
        "hydrology": (
            "Hydrological parameters are missing. "
            "Please specify: annual rainfall in mm, or moisture regime "
            "(e.g., 'low / semi-arid', 'moderate subhumid', 'high / humid')."
        ),
        "vegetation": (
            "Land use and vegetation matrix must be defined. "
            "Please specify: current crop (e.g., 'monoculture wheat'), "
            "land use type (e.g., 'degraded rangeland', 'mixed agroforestry'), "
            "or dominant vegetation cover."
        ),
    }

    def __init__(self, reasoning_engine: Optional[ReasoningEngine] = None):
        self.engine = reasoning_engine or ReasoningEngine()
        self.sessions: Dict[str, EcologicalSession] = {}

    def get_or_create_session(
        self, session_id: Optional[str] = None
    ) -> EcologicalSession:
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = EcologicalSession(new_id)
            return self.sessions[new_id]
        return self.sessions[session_id]

    # ──────────────────────────────────────────────────────────────────────────
    # ENTITY EXTRACTION — Natural Language Parameter Parser
    # ──────────────────────────────────────────────────────────────────────────

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extracts structured environmental parameters from natural language text.
        Covers all relevant ecological variables for scientific analysis.
        """
        extracted: Dict[str, Any] = {}
        lower = text.lower()

        # ── Soil Organic Carbon ──────────────────────────────────────────────
        soc_match = re.search(
            r'(?:soil\s+organic\s+carbon|soc)\s*[:=]?\s*([0-9]*\.?[0-9]+)\s*%?',
            lower
        )
        if soc_match:
            try:
                extracted["soil_organic_carbon"] = float(soc_match.group(1))
            except ValueError:
                pass
        elif any(kw in lower for kw in ("low carbon", "depleted carbon", "carbon depleted", "poor soil")):
            extracted["soil_organic_carbon"] = 0.4
        elif "very low soc" in lower or "critically low" in lower:
            extracted["soil_organic_carbon"] = 0.2

        # ── Rainfall / Hydrology ─────────────────────────────────────────────
        rain_mm = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:mm|millimetres?|millimeters?)', lower)
        if rain_mm:
            try:
                extracted["rainfall_mm"] = float(rain_mm.group(1))
            except ValueError:
                pass

        if any(kw in lower for kw in ("low rainfall", "rainfall: low", "arid", "dryland", "dry land", "drought prone")):
            extracted["rainfall"] = "low"
        elif any(kw in lower for kw in ("high rainfall", "heavy rain", "humid")):
            extracted["rainfall"] = "high"
        elif any(kw in lower for kw in ("moderate rainfall", "subhumid", "sub-humid")):
            extracted["rainfall"] = "moderate"
        elif "semi-arid" in lower or "semi arid" in lower:
            extracted["rainfall"] = "low"
            if "region" not in extracted:
                extracted["region"] = "semi-arid"

        # ── Crop / Vegetation ────────────────────────────────────────────────
        crop_match = re.search(
            r'(?:crop|growing|cultivating|land\s+under)\s*[:=]?\s*([a-z\s]+?)(?:,|\.|$|\n)', lower
        )
        if crop_match:
            crop_val = crop_match.group(1).strip()
            if len(crop_val) > 1:
                extracted["crop"] = crop_val

        # Specific crop keywords
        if "monoculture wheat" in lower or "wheat monoculture" in lower:
            extracted["crop"] = "monoculture wheat"
        elif "wheat" in lower and "monoculture" not in lower:
            extracted["crop"] = "wheat"
        elif "monoculture" in lower:
            extracted["land_use"] = "monoculture"
        elif any(kw in lower for kw in ("corn", "maize")):
            extracted["crop"] = "monoculture maize"
        elif "soybean" in lower or "soy" in lower:
            extracted["crop"] = "soybean monoculture"
        elif "cotton" in lower:
            extracted["crop"] = "cotton"
        elif any(kw in lower for kw in ("pasture", "rangeland", "grassland")):
            extracted["crop"] = "pasture/rangeland"
        elif "pearl millet" in lower or "bajra" in lower:
            extracted["crop"] = "pearl millet"
        elif any(kw in lower for kw in ("overgraz", "degraded pasture", "bare land", "bare soil")):
            extracted["land_use"] = "degraded / overgrazed rangeland"

        # ── Region / Climate Zone ────────────────────────────────────────────
        region_match = re.search(
            r'region\s*[:=]?\s*([a-z\s\-]+?)(?:,|\.|$|\n)', lower
        )
        if region_match:
            r_val = region_match.group(1).strip()
            if len(r_val) > 1:
                extracted["region"] = r_val

        for kw in ("semi-arid", "semi arid", "mediterranean", "tropical", "temperate",
                   "sahelian", "deccan", "thar", "boreal", "arid"):
            if kw in lower and "region" not in extracted:
                extracted["region"] = kw
                break

        # Known location → region mapping
        location_map = {
            "rajasthan": "semi-arid / thar desert margin",
            "gujarat": "semi-arid tropical",
            "deccan": "semi-arid deccan plateau",
            "sahel": "sahelian semi-arid savanna",
            "great plains": "temperate semi-arid steppe",
            "mediterranean": "mediterranean dry-summer",
            "amazon": "tropical humid",
            "karnataka": "semi-arid tropical",
        }
        for loc, mapped_region in location_map.items():
            if loc in lower and "region" not in extracted:
                extracted["region"] = mapped_region
                break

        # ── Soil pH ──────────────────────────────────────────────────────────
        ph_match = re.search(r'\bph\s*[:=]?\s*([0-9]*\.?[0-9]+)', lower)
        if ph_match:
            try:
                extracted["ph"] = float(ph_match.group(1))
            except ValueError:
                pass
        elif "acidic soil" in lower or "acid soil" in lower:
            extracted["ph"] = 4.8
        elif "alkaline soil" in lower:
            extracted["ph"] = 8.5

        # ── Bulk Density ─────────────────────────────────────────────────────
        bd_match = re.search(r'bulk\s*density\s*[:=]?\s*([0-9]*\.?[0-9]+)', lower)
        if bd_match:
            try:
                extracted["bulk_density"] = float(bd_match.group(1))
            except ValueError:
                pass
        elif any(kw in lower for kw in ("compacted", "hardpan", "compaction")):
            extracted["bulk_density"] = 1.6

        # ── Erosion Rate ─────────────────────────────────────────────────────
        erosion_match = re.search(
            r'erosion\s*(?:rate)?\s*[:=]?\s*([0-9]*\.?[0-9]+)\s*(?:t/ha|tonnes)', lower
        )
        if erosion_match:
            try:
                extracted["erosion_rate"] = float(erosion_match.group(1))
            except ValueError:
                pass
        elif any(kw in lower for kw in ("severe erosion", "gully erosion", "heavy erosion")):
            extracted["erosion_rate"] = 12.0

        # ── Species Richness ─────────────────────────────────────────────────
        sp_match = re.search(r'(\d+)\s*(?:plant\s+)?species', lower)
        if sp_match:
            try:
                extracted["species_richness"] = float(sp_match.group(1))
            except ValueError:
                pass

        # ── Geo-Coordinates ──────────────────────────────────────────────────
        coord_match = re.search(
            r'([-+]?\d{1,2}\.?\d*)[,\s°N]*\s*([-+]?\d{1,3}\.?\d*)\s*°?[EW]?', text
        )
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    extracted["coordinates"] = {"lat": lat, "lon": lon}
            except ValueError:
                pass

        return extracted

    # ──────────────────────────────────────────────────────────────────────────
    # COMPLETENESS VALIDATION
    # ──────────────────────────────────────────────────────────────────────────

    def validate_completeness(
        self, state: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validates whether the accumulated environmental state has sufficient
        parameters across >= 2 key scientific dimensions for rigorous analysis.

        Returns:
            (is_complete, missing_dimensions, intake_questions)
        """
        has_dim: Dict[str, bool] = {}

        for dim, keys in self.REQUIRED_DIMENSIONS.items():
            has_dim[dim] = any(state.get(k) is not None for k in keys)

        # Coordinates can substitute for soil and hydrology baselines
        if state.get("coordinates"):
            has_dim["soil"] = True
            has_dim["hydrology"] = True

        missing_dims = [dim for dim, present in has_dim.items() if not present]
        questions = [self.INTAKE_QUESTIONS[dim] for dim in missing_dims]

        # Complete if at most 1 dimension is missing and at least 1 is present
        is_complete = len(missing_dims) <= 1 and any(has_dim.values())

        return is_complete, missing_dims, questions

    # ──────────────────────────────────────────────────────────────────────────
    # MAIN PROCESSING ENTRY POINT
    # ──────────────────────────────────────────────────────────────────────────

    def process_turn(
        self,
        user_text: str,
        session_id: Optional[str] = None,
        structured_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processes one intake turn of the ecological assessment workflow.

        - Extracts environmental parameters from natural language
        - Merges with structured payload if provided
        - Validates completeness across required scientific dimensions
        - Asks targeted intake questions if data is insufficient
        - Triggers full scientific analysis when data is adequate
        """
        session = self.get_or_create_session(session_id)
        session.add_exchange("user", user_text)

        # Extract entities from free-text
        extracted = self.extract_parameters(user_text)
        session.update_state(extracted)

        # Merge explicit structured payload
        if structured_payload:
            session.update_state(structured_payload)

        current_state = session.accumulated_state

        # Validate completeness
        is_complete, missing_dims, questions = self.validate_completeness(current_state)

        if not is_complete:
            # Generate scientific intake clarification
            missing_str = " and ".join(
                dim.title().replace("_", " ") for dim in missing_dims
            )
            clarification = (
                f"Site assessment requires additional environmental parameters to conduct a rigorous multi-metric analysis. "
                f"Missing dimensions: {missing_str}.\n\n"
                f"To ensure high-confidence diagnosis, could you please provide:\n"
                + "\n".join(f"• {q}" for q in questions)
                + "\n\nAlternatively, provide geographic coordinates "
                  "(latitude, longitude) to derive baseline parameters from "
                  "spatial biome classification."
            )
            session.add_exchange("scientist", clarification)
            return {
                "session_id": session.session_id,
                "status": "awaiting_clarification",
                "is_complete": False,
                "missing_parameters": missing_dims,
                "missing_dimensions": missing_dims,
                "intake_questions": questions,
                "response_text": clarification,
                "accumulated_state": current_state,
                "state_summary": session.get_state_summary(),
                "turn_count": session.turn_count,
                "analysis": None,
            }

        # Full scientific analysis
        analysis = self.engine.analyze_ecosystem(current_state)
        session.last_analysis = analysis

        # Render full scientific narrative
        narrative = self.engine.generate_scientific_narrative(analysis)
        session.add_exchange("scientist", narrative)

        return {
            "session_id": session.session_id,
            "status": "completed",
            "is_complete": True,
            "missing_parameters": [],
            "missing_dimensions": [],
            "intake_questions": [],
            "response_text": narrative,
            "accumulated_state": current_state,
            "state_summary": session.get_state_summary(),
            "turn_count": session.turn_count,
            "analysis": analysis,
        }

    def reset_session(self, session_id: str) -> EcologicalSession:
        """Clears accumulated state and starts a fresh assessment."""
        new_session = EcologicalSession(session_id)
        self.sessions[session_id] = new_session
        return new_session


# Alias for backward compatibility and test suites
DialogueManager = ScientificSessionManager

