import os

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import scan, upload, interpret, report, feedback, qa, agent
from .security import require_site_password

# Load backend/.env explicitly \u2014 don't rely on the process's current
# working directory, since `uvicorn app.main:app` can be launched from
# different places depending on the terminal/IDE.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="Digital Archaeologist API",
    description="Backend for the Digital Archaeologist project.",
    version="0.1.0",
)

# Allow the Next.js dev server to call this API from the browser.
# ALLOWED_ORIGINS (comma-separated) lets a deployed frontend be added
# without touching this file again \u2014 localhost stays allowed too so
# local development keeps working unchanged.
_extra_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *_extra_origins,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Every route that can upload, execute, or call an LLM sits behind the
# shared site password (see security.py). It's a no-op locally unless
# SITE_PASSWORD is set, so nothing changes for local development.
_gate = [Depends(require_site_password)]
app.include_router(upload.router, dependencies=_gate)
app.include_router(scan.router, dependencies=_gate)
app.include_router(interpret.router, dependencies=_gate)
app.include_router(report.router, dependencies=_gate)
app.include_router(feedback.router, dependencies=_gate)
app.include_router(qa.router, dependencies=_gate)
app.include_router(agent.router, dependencies=_gate)



@app.get("/api/health")
def health_check():
    """Phase 1: proves the frontend and backend can talk to each other.
    Deliberately NOT behind the password gate, so hosting platforms can
    still health-check the service."""
    return {
        "status": "ok",
        "service": "digital-archaeologist-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
def root():
    return {"message": "Digital Archaeologist API is running. Try /api/health"}

