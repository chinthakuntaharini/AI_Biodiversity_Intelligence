# Darukaa.Earth — AI Biodiversity Intelligence Platform

An intelligent, knowledge-driven environmental conversational reasoning system designed for ecological restoration, multi-metric environmental analysis, and biodiversity enhancement.

Developed for the **Darukaa.Earth AI Biodiversity Intelligence Hackathon Challenge**.

---

## 1. System Overview & Objective

The platform functions as an **AI Environmental Scientist**, evaluating real-world agro-ecological challenges through multi-variable scientific synthesis rather than generic conversational prompts.

### Key Capabilities
- **Retrievable Knowledge Layer (RAG & Semantic Index)**: Structured knowledge base indexing peer-reviewed literature, UN FAO technical manuals, IPCC AR6 assessments, and IPBES reports across 5 domains: Soil Health, Land Use & Land Cover, Biodiversity Indicators, Climate Factors, and Anthropogenic Impacts.
- **Coupled Multi-Metric Reasoning**: Connects at least 3 environmental variables simultaneously (e.g., Soil Organic Carbon $\leftrightarrow$ Water Holding Capacity $\leftrightarrow$ Microbial & Earthworm Diversity $\leftrightarrow$ Pollinator Guilds $\leftrightarrow$ Crop Matrix) to formulate non-obvious, actionable interventions with measurable quantitative estimates.
- **Conversational Intelligence with Clarifying Logic**: Detects underspecified inputs (e.g., *"Biodiversity is declining on my land"*) and dynamically queries for essential missing ecological parameters before prescribing interventions.
- **Multi-Turn Session Memory**: Preserves context and updates the environmental state vector across multi-turn user dialogues.
- **Flexible Input Modalities & Spatial Context**: Accepts natural language queries, structured JSON payloads, and geographic coordinates (resolving biomes, Köppen climate classes, and baseline precipitation).
- **Standardized Evidence-Backed Outputs**: Delivers actionable prescriptions, scientific mechanisms, multi-metric impacts, time horizons (short/medium/long-term), confidence levels, and authoritative citations.

---

## 2. Architecture & Data Schema

### High-Level Architecture

```
                                  +---------------------------------------+
                                  |           User Interfaces             |
                                  |   Web UI (Vanilla)  /  CLI  /  REST   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       FastAPI Application Layer       |
                                  |          (app/main.py, schemas)       |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     Dialogue & Memory Manager         |
                                  |      (core/dialogue_manager.py)       |
                                  +----------+-----------------+----------+
                                             |                 |
                       (If input incomplete) |                 | (If input complete)
                                             v                 v
                                  +--------------------+  +--------------------------------+
                                  | Clarifying Question|  |   Multi-Metric Reasoning Engine|
                                  |     Generator      |  |   (core/reasoning_engine.py)   |
                                  +--------------------+  +---+------------------------+---+
                                                              |                        |
                                                              v                        v
                                            +--------------------+    +--------------------+
                                            | Spatial Resolver   |    | Knowledge Base RAG |
                                            | (Bio-Climate Map)  |    | (BM25 Index + Data)|
                                            +--------------------+    +--------------------+
```

### Directory Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated CI/CD pipeline (pytest on Py3.10-3.12)
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI REST API & static web mount
│   └── schemas.py                 # Pydantic data validation schemas
├── core/
│   ├── __init__.py
│   ├── dialogue_manager.py        # Conversational memory & input completeness checker
│   ├── knowledge_base.py          # BM25 & semantic RAG retrieval engine
│   ├── reasoning_engine.py        # Multi-metric ecological reasoning & synthesis
│   └── spatial_resolver.py        # Geo-coordinates to biome & climate classifier
├── data/
│   ├── knowledge_store/           # Curated peer-reviewed datasets & reports
│   │   ├── soil_health.json       # SOC, microbial biomass, pH, bulk density
│   │   ├── land_cover.json        # Agroforestry, silvopasture, vegetative buffers
│   │   ├── biodiversity.json      # Pollinators, earthworms, trophic networks
│   │   ├── climate_water.json     # Aridity, hydrology, drought buffering
│   │   └── human_impact.json      # Chemical runoff, buffer strips, IPM
│   └── spatial_biomes.json        # Global ecoregions, Köppen classes & baselines
├── static/
│   ├── index.html                 # Scientific dashboard UI
│   ├── styles.css                 # Theme & glassmorphism styling
│   └── app.js                     # Dynamic chat, diagnostics, and RAG search
├── tests/
│   ├── __init__.py
│   ├── test_api.py                # REST API integration tests
│   ├── test_dialogue_manager.py   # Multi-turn memory & clarification tests
│   ├── test_knowledge_base.py     # Corpus coverage & RAG retrieval tests
│   └── test_reasoning_engine.py   # Benchmark scenario & multi-metric tests
├── cli.py                         # Command-line interface
├── run.py                         # One-click server launcher
├── requirements.txt               # Pinned Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

### Knowledge Base Schema Example

```json
{
  "id": "LAND-001",
  "domain": "land_cover",
  "topic": "Agroforestry, Intercropping, and Structural Heterogeneity in Croplands",
  "key_variables": ["land_use_type", "crop_diversity", "canopy_cover_pct"],
  "scientific_summary": "Transitioning from monoculture cropping to multi-strata agroforestry...",
  "interventions": [
    {
      "name": "Alley Cropping and Perennial Nitrogen-Fixing Tree Belts",
      "suitable_conditions": {"land_use": "monoculture_cropland", "climate": "semi_arid_or_subhumid"},
      "mechanism": "Planting drought-hardy leguminous trees in hedgerow alleys...",
      "quantitative_impact": {
        "crop_yield_stability_gain": "15% - 25% under drought anomaly years",
        "soil_organic_carbon_gain": "+0.25% - 0.40% over 5 years",
        "wild_pollinator_richness_gain": "+40% - 65% species richness increase"
      },
      "time_horizon": "medium to long-term (3-7 years)",
      "confidence_level": 0.94,
      "citations": ["FAO (2020)...", "IPCC (2022)..."]
    }
  ]
}
```

---

## 3. Local Setup & Installation

### Prerequisites
- Python 3.10 or higher
- PowerShell, Bash, or Command Prompt

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/darukaa-earth-biointelligence.git
cd "darukaa-earth-biointelligence"
```

### Step 2: Create & Activate Virtual Environment
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. Running the Application

### Option A: Web Application & REST API
Start the FastAPI server and open the web dashboard:
```bash
python run.py
```
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Interactive Terminal CLI
Run an interactive session in your terminal:
```bash
python cli.py interactive
```

### Option C: Run Benchmark Test Case
Execute the hackathon reference case (0.3% SOC, low rainfall, wheat monoculture, semi-arid):
```bash
python cli.py benchmark
```

### Option D: Query Knowledge Base
Inspect knowledge store chunks and citations from the command line:
```bash
python cli.py query-kb --query "soil organic carbon agroforestry"
```

---

## 5. Running Automated Tests

Run the full test suite with either `pytest` or `unittest`:

```bash
# Using pytest
pytest -v

# Using Python unittest
python -m unittest discover -s tests -v
```

All 12 test cases validate:
1. Benchmark scenario evaluation and multi-metric reasoning.
2. Incomplete input detection and clarifying question generation.
3. Multi-turn dialogue memory.
4. RAG knowledge store coverage and retrieval scoring.
5. Spatial coordinates resolution.
6. REST API endpoint responses.

---

## 6. CI/CD Pipeline

The repository includes a GitHub Actions configuration in `.github/workflows/ci.yml`. On every push and pull request, it:
1. Sets up Python across versions 3.10, 3.11, and 3.12.
2. Installs dependencies from `requirements.txt`.
3. Executes the full `pytest` test suite to verify 100% passing tests.

---

## 7. Submission Checklist & Access

- **GitHub Repository**: Accessible publicly or shared with hackathon reviewers:
  - `ankita.dasgupta@darukaa.com`
  - `harsh.kumar@darukaa.com`
  - `utkarsh.gauniyal@darukaa.com`
  - `guneet.mutreja@darukaa.com`
- **Dependencies**: Pinned in `requirements.txt`.
- **Zero External API Lock-in**: Fully functional standalone with local RAG and deterministic reasoning engine.
