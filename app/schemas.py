"""
Pydantic Schemas for the Darukaa.Earth Environmental Intelligence API.
Covers all request/response structures for ecological assessment,
spatial biome resolution, and knowledge base retrieval.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Shared Sub-models
# ──────────────────────────────────────────────────────────────────────────────

class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees (WGS84)")
    lon: float = Field(..., description="Longitude in decimal degrees (WGS84)")


class MetricImpact(BaseModel):
    metric: str = Field(..., description="Environmental metric name")
    projected_change: str = Field(..., description="Quantified projected change with units")
    dimension: str = Field(..., description="Ecological dimension (e.g., Soil Health, Hydrology)")


class Prescription(BaseModel):
    title: str
    priority: str
    action: str
    scientific_mechanism: str
    multi_metric_impacts: List[MetricImpact]
    time_horizon: str
    confidence_level: str
    citations: List[str]


# ──────────────────────────────────────────────────────────────────────────────
# /api/scientist/analyze  (Structured multi-variable analysis)
# ──────────────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    # Core soil parameters
    soil_organic_carbon: Optional[float] = Field(
        None, description="Soil Organic Carbon %, e.g. 0.3 (critical <0.5, low <1.0, moderate <2.0)"
    )
    ph: Optional[float] = Field(
        None, description="Soil pH level (optimal range 6.0–7.0 for most crops)"
    )
    bulk_density: Optional[float] = Field(
        None, description="Soil bulk density g/cm³ (>1.4 indicates compaction)"
    )
    erosion_rate: Optional[float] = Field(
        None, description="Annual soil erosion rate in t/ha/yr (>5 = high risk)"
    )
    soil_type: Optional[str] = Field(
        None, description="Dominant soil classification, e.g. 'Aridisol', 'Vertisol'"
    )

    # Hydrological parameters
    rainfall: Optional[str] = Field(
        None, description="Moisture regime: 'low', 'moderate', or 'high'"
    )
    rainfall_mm: Optional[float] = Field(
        None, description="Annual precipitation in millimetres"
    )

    # Vegetation / land use
    crop: Optional[str] = Field(
        None, description="Current crop or agronomic system, e.g. 'monoculture wheat'"
    )
    land_use: Optional[str] = Field(
        None, description="Land use / land cover category, e.g. 'degraded rangeland'"
    )
    ndvi: Optional[float] = Field(
        None, description="Normalised Difference Vegetation Index (0–1)"
    )
    species_richness: Optional[float] = Field(
        None, description="Observed plant species richness at site"
    )

    # Climatic context
    region: Optional[str] = Field(
        None, description="Climatic / ecological region, e.g. 'semi-arid', 'Mediterranean'"
    )

    # Spatial context
    coordinates: Optional[Coordinates] = Field(
        None, description="Geographic coordinates for biome-based enrichment"
    )

    model_config = {"extra": "allow"}


class RiskProfile(BaseModel):
    soil_carbon: str
    hydrology: str
    biodiversity: str
    soil_chemistry: str
    land_use: str
    erosion: str


class NexusAnalysis(BaseModel):
    summary: str
    primary_stressor: str
    degraded_dimensions: List[str]
    interaction_chains: List[str]
    system_trajectory: str


class AnalyzeResponse(BaseModel):
    environmental_state: Dict[str, Any]
    variables_evaluated: List[str]
    variable_count: int
    risk_profile: Dict[str, str]
    multi_metric_nexus: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    knowledge_evidence: List[Dict[str, Any]]


# ──────────────────────────────────────────────────────────────────────────────
# /api/scientist/intake  (Conversational multi-turn intake)
# ──────────────────────────────────────────────────────────────────────────────

class IntakeRequest(BaseModel):
    """
    Multi-turn scientific intake request.
    Send natural language descriptions of the ecosystem;
    the system will request missing parameters until analysis can proceed.
    """
    message: str = Field(
        ...,
        description="Natural language description of ecosystem conditions, e.g. "
                    "'Soil organic carbon: 0.3%, low rainfall, monoculture wheat, semi-arid region'",
        examples=["SOC is 0.3%, low rainfall, wheat monoculture, semi-arid region"],
    )
    session_id: Optional[str] = Field(
        None,
        description="Persistent session identifier for multi-turn assessment. "
                    "Omit to start a new session.",
    )
    structured_inputs: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional structured environmental parameters to merge with the message.",
    )

    # Backwards-compatible alias
    @property
    def structured_payload(self) -> Optional[Dict[str, Any]]:
        return self.structured_inputs


class IntakeResponse(BaseModel):
    session_id: str
    status: str = Field(
        ..., description="'awaiting_clarification' | 'completed' | 'awaiting_parameters' | 'analysis_complete'"
    )
    is_complete: bool
    missing_dimensions: List[str] = []
    missing_parameters: List[str] = []
    intake_questions: List[str] = []
    response_text: str
    accumulated_state: Dict[str, Any] = {}
    state_summary: str = ""
    turn_count: int = 0
    analysis: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


# Backwards-compatible aliases
ChatRequest  = IntakeRequest
ChatResponse = IntakeResponse


# ──────────────────────────────────────────────────────────────────────────────
# /api/spatial/lookup
# ──────────────────────────────────────────────────────────────────────────────

class SpatialLookupRequest(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees (WGS84)")
    longitude: float = Field(..., description="Longitude in decimal degrees (WGS84)")


# ──────────────────────────────────────────────────────────────────────────────
# /api/knowledge/query
# ──────────────────────────────────────────────────────────────────────────────

class KnowledgeQueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="Scientific search query, e.g. 'agroforestry soil organic carbon semi-arid'",
    )
    domain: Optional[str] = Field(
        None,
        description="Filter by knowledge domain: 'soil_health', 'land_cover', "
                    "'biodiversity_indicators', 'climate_factors', 'human_impact'",
    )
    top_k: int = Field(3, ge=1, le=20, description="Number of knowledge chunks to retrieve")
