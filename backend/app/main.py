# FastAPI application entry point.
# Wires CORS middleware, the health route, and the analyze route.
# Start with: uvicorn app.main:app --reload (from the backend/ directory)

import sys
from pathlib import Path

# Ensure backend directory is in sys.path regardless of current working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_analyze import router as analyze_router
from app.api.routes_tts import router as tts_router

app = FastAPI(
    title="Job Offer Checker API",
    version="0.1.0",
)


@app.get("/")
@app.head("/")
def service_root():
    return {"status": "ok", "service": "Mig_Guard"}

is_wildcard = "*" in settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(tts_router, prefix="/api")