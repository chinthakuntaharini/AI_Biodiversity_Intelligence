"""
Darukaa.Earth Environmental Intelligence Platform — FastAPI Application.

REST API and web dashboard for the ecological scientific engine.
Provides structured environmental analysis, multi-turn intake,
spatial biome resolution, and knowledge base retrieval.
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    IntakeRequest, IntakeResponse,
    AnalyzeRequest,
    SpatialLookupRequest,
    KnowledgeQueryRequest,
)
from core.knowledge_base import KnowledgeBase
from core.spatial_resolver import SpatialResolver
from core.reasoning_engine import ReasoningEngine
from core.dialogue_manager import ScientificSessionManager

# ──────────────────────────────────────────────────────────────────────────────
# Application Setup
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Darukaa.Earth Environmental Intelligence Platform",
    description=(
        "AI-powered ecological reasoning engine for multi-metric environmental "
        "analysis, biodiversity assessment, and evidence-backed restoration planning. "
        "Synthesises >= 3 environmental variables simultaneously (Soil, Hydrology, "
        "Biodiversity, Land Use, Climate) grounded in FAO, IPCC, IPBES, and USDA-NRCS literature."
    ),
    version="2.0.0",
    contact={
        "name": "Darukaa.Earth Environmental Science Team",
        "url": "https://darukaa.earth",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Service Initialisation
# ──────────────────────────────────────────────────────────────────────────────

kb       = KnowledgeBase()
spatial  = SpatialResolver()
engine   = ReasoningEngine(knowledge_base=kb, spatial_resolver=spatial)
intake   = ScientificSessionManager(reasoning_engine=engine)

# ──────────────────────────────────────────────────────────────────────────────
# Static Files (Scientific Dashboard)
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(
        "<h1>Darukaa.Earth Environmental Intelligence Platform</h1>"
        "<p>API is running. Visit <a href='/docs'>/docs</a> for the OpenAPI interface.</p>"
    )


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """System health and corpus statistics."""
    return {
        "status": "healthy",
        "service": "Darukaa.Earth Environmental Intelligence Platform",
        "version": "2.0.0",
        "engine": "Multi-Metric Ecological Reasoning Engine v2",
        "indexed_documents": len(kb.documents),
        "knowledge_base": {
            "indexed_documents": len(kb.documents),
            "indexed_domains": kb.get_all_domains(),
            "total_citations": len(kb.get_all_citations()),
        },
        "spatial_resolver": {
            "biome_profiles": len(spatial.biomes),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# CORE SCIENTIFIC ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/api/scientist/analyze",
    tags=["Scientific Analysis"],
    summary="Structured Multi-Variable Ecological Analysis",
    response_description="Full ecological assessment with risk profile, nexus analysis, and intervention prescriptions",
)
async def analyze_ecosystem(request: AnalyzeRequest):
    """
    **Primary scientific analysis endpoint.**

    Accepts structured environmental parameters and returns a complete
    ecological field assessment including:

    - **Risk Profile**: Degradation severity classification for each environmental dimension
    - **Multi-Metric Nexus**: Causal interaction chains across soil, hydrology, and biodiversity
    - **Intervention Prescriptions**: >= 3 evidence-backed recommendations with quantified multi-metric impacts
    - **Scientific Evidence**: Retrieved knowledge chunks with peer-reviewed citations

    Evaluates >= 3 environmental variables simultaneously:
    Soil Organic Carbon ↔ Hydrology ↔ Biodiversity ↔ Land Use ↔ Climate

    **Example minimum input:**
    ```json
    {
      "soil_organic_carbon": 0.3,
      "rainfall": "low",
      "crop": "monoculture wheat",
      "region": "semi-arid"
    }
    ```
    """
    try:
        state = request.model_dump(exclude_none=True)
        if "coordinates" in state and state["coordinates"]:
            state["coordinates"] = request.coordinates.model_dump()
        analysis = engine.analyze_ecosystem(state)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/analyze",
    tags=["Scientific Analysis"],
    summary="Alias: Structured Multi-Variable Ecological Analysis",
    include_in_schema=False,
)
async def analyze_alias(request: AnalyzeRequest):
    return await analyze_ecosystem(request)



@app.post(
    "/api/scientist/analyze/narrative",
    tags=["Scientific Analysis"],
    summary="Full Ecological Assessment Report (Narrative Format)",
    response_description="Plain-text scientific field assessment report",
)
async def analyze_with_narrative(request: AnalyzeRequest):
    """
    Performs the full ecological analysis and returns both structured data
    and a formatted scientific field assessment report.

    The narrative output mirrors a professional environmental scientist's
    field report: site classification, risk profile, nexus analysis,
    and ranked intervention prescriptions with citations.
    """
    try:
        state = request.model_dump(exclude_none=True)
        if "coordinates" in state and state["coordinates"]:
            state["coordinates"] = request.coordinates.model_dump()
        analysis = engine.analyze_ecosystem(state)
        narrative = engine.generate_scientific_narrative(analysis)
        return {
            "narrative": narrative,
            "structured": analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/scientist/intake",
    response_model=IntakeResponse,
    tags=["Scientific Analysis"],
    summary="Multi-Turn Ecological Parameter Intake",
)
async def scientific_intake(request: IntakeRequest):
    """
    **Multi-turn natural language parameter intake endpoint.**

    Accepts free-text descriptions of ecosystem conditions.
    Extracts environmental parameters, validates data completeness
    across required scientific dimensions, and requests targeted
    clarification when inputs are insufficient.

    Once sufficient parameters are accumulated across a session,
    automatically triggers the full ecological analysis.

    **Session continuity:** Include `session_id` from previous response
    to maintain parameter context across multiple turns.

    **Example queries:**
    - *"Biodiversity is declining on my farm"* → requests soil, rainfall, land-use data
    - *"SOC 0.3%, low rainfall, monoculture wheat, semi-arid"* → full analysis
    - *"26.28, 73.02 — pearl millet farming"* → spatial enrichment + analysis
    """
    try:
        result = intake.process_turn(
            user_text=request.message,
            session_id=request.session_id,
            structured_payload=request.structured_inputs,
        )
        return IntakeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Backwards-compatible alias
@app.post(
    "/api/chat",
    response_model=IntakeResponse,
    tags=["Scientific Analysis"],
    summary="Alias: Multi-Turn Intake (backwards compatible)",
    include_in_schema=False,
)
async def chat_alias(request: IntakeRequest):
    return await scientific_intake(request)


# ──────────────────────────────────────────────────────────────────────────────
# SPATIAL ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/api/spatial/lookup",
    tags=["Spatial Intelligence"],
    summary="Geo-Coordinate → Biome & Baseline Metrics Resolution",
)
async def spatial_lookup(request: SpatialLookupRequest):
    """
    Resolves geographic coordinates to eco-region classification,
    Köppen-Geiger climate class, and baseline environmental metrics.

    Returns:
    - Biome identification and zone name
    - Köppen climate classification
    - Baseline soil, hydrology, and vegetation metrics
    - Native vegetation taxa
    """
    try:
        return spatial.resolve(request.latitude, request.longitude)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/spatial/biomes",
    tags=["Spatial Intelligence"],
    summary="List All Registered Biome Profiles",
)
async def list_biomes():
    """Returns the complete list of registered global biome profiles with baseline metrics."""
    try:
        return {
            "total_biomes": len(spatial.biomes),
            "biomes": [
                {
                    "id": b["id"],
                    "name": b["name"],
                    "koppen_classes": b.get("koppen_classes", []),
                    "baseline_metrics": b.get("baseline_metrics", {}),
                }
                for b in spatial.biomes
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@app.post(
    "/api/knowledge/query",
    tags=["Knowledge Base"],
    summary="Query Peer-Reviewed Scientific Knowledge Base",
)
async def query_knowledge(request: KnowledgeQueryRequest):
    """
    Retrieves the most relevant scientific knowledge chunks using BM25
    retrieval from the indexed peer-reviewed corpus.

    **Corpus domains:**
    - `soil_health` — SOC, microbial biomass, pH, bulk density
    - `land_cover` — Agroforestry, silvopasture, vegetative buffers
    - `biodiversity_indicators` — Pollinators, earthworms, trophic networks
    - `climate_factors` — Aridity, hydrology, drought buffering
    - `human_impact` — Chemical runoff, buffer strips, IPM

    **Sources:** FAO, IPCC AR6, IPBES, USDA-NRCS
    """
    try:
        chunks = kb.retrieve(request.query, domain=request.domain, top_k=request.top_k)
        return {
            "query": request.query,
            "domain_filter": request.domain,
            "results_count": len(chunks),
            "results": chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/knowledge/overview",
    tags=["Knowledge Base"],
    summary="Knowledge Base Corpus Overview",
)
async def knowledge_overview():
    """
    Returns an overview of the indexed scientific corpus:
    domains, document count, citation inventory.
    """
    try:
        all_citations = kb.get_all_citations()
        return {
            "domains": kb.get_all_domains(),
            "total_documents": len(kb.documents),
            "total_citations": len(all_citations),
            "sample_citations": all_citations[:10],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/knowledge/domains",
    tags=["Knowledge Base"],
    summary="List Knowledge Domains with Document Counts",
)
async def knowledge_domains():
    """Lists all knowledge domains with their document counts."""
    try:
        domain_counts: dict = {}
        for doc in kb.documents:
            domain_counts[doc.domain] = domain_counts.get(doc.domain, 0) + 1
        return {
            "domains": [
                {"domain": d, "document_count": c}
                for d, c in sorted(domain_counts.items())
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
