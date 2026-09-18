"""
Darukaa.Earth AI Biodiversity Intelligence Platform - Server Runner.
Starts the FastAPI application and web dashboard on http://localhost:8000.
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print(" Starting Darukaa.Earth AI Biodiversity Intelligence Platform")
    print(" Dashboard URL: http://localhost:8000")
    print(" OpenAPI Docs:  http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
