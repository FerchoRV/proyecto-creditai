from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(title="CreditAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://creditai:creditai@db:5432/creditai",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "creditai-backend"}


@app.get("/health/db")
def health_db() -> dict[str, Any]:
    url = get_database_url()
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except SQLAlchemyError as exc:
        return {"status": "error", "database": "unreachable", "detail": str(exc.__class__.__name__)}
    finally:
        engine.dispose()


@app.get("/api/v1")
def api_root() -> dict[str, str]:
    return {"message": "CreditAI API v1", "docs": "/docs"}
