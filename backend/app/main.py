from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.routers import auth, invitations, solicitudes, users

app = FastAPI(title="CreditAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(invitations.router)
app.include_router(solicitudes.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "creditai-backend"}


@app.get("/health/db")
def health_db() -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except SQLAlchemyError as exc:
        return {
            "status": "error",
            "database": "unreachable",
            "detail": str(exc.__class__.__name__),
        }


@app.get("/api/v1")
def api_root() -> dict[str, str]:
    return {"message": "CreditAI API v1", "docs": "/docs"}
