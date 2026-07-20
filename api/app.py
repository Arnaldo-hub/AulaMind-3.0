"""
===========================================================
AulaMind Enterprise 3.0

REST API

FastAPI Application

Semana 9.1
===========================================================
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
try:
    from api.routers.dashboard import router as dashboard_router
except ImportError:
    dashboard_router = None

try:
    from api.routers.audit import router as audit_router
except ImportError:
    audit_router = None

try:
    from api.routers.planning import router as planning_router
except ImportError:
    planning_router = None

try:
    from api.routers.curriculum import router as curriculum_router
except ImportError:
    curriculum_router = None


APP_VERSION = "9.1"


app = FastAPI(
    title="AulaMind Enterprise 3.0 API",
    description=(
        "API oficial de AulaMind Enterprise 3.0 "
        "para consumo por Dashboard, Frontend "
        "y aplicaciones externas."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/", tags=["System"])
def root():

    return {

        "application": "AulaMind Enterprise 3.0",

        "version": APP_VERSION,

        "status": "running",

        "documentation": "/docs",

    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
def health():

    return {

        "status": "healthy",

        "api": True,

        "version": APP_VERSION,

    }


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

if dashboard_router:
    app.include_router(
        dashboard_router,
        prefix="/dashboard",
        tags=["Dashboard"],
    )

if audit_router:
    app.include_router(
        audit_router,
        prefix="/audit",
        tags=["Audit"],
    )

if planning_router:
    app.include_router(
        planning_router,
        prefix="/planning",
        tags=["Planning"],
    )

if curriculum_router:
    app.include_router(
        curriculum_router,
        prefix="/curriculum",
        tags=["Curriculum"],
    )


# ---------------------------------------------------------
# Local execution
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )