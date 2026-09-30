from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://creditai:creditai@db:5432/creditai",
    )
    engine = create_engine(database_url, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Ensure schema exists (migrations run on container start; recreate for isolation).
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    # Cleanup users created in this test session by unique emails is enough;
    # also wipe table for deterministic runs inside shared DB.
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM timeline_events"))
        conn.execute(text("DELETE FROM invitaciones"))
        conn.execute(text("DELETE FROM solicitudes"))
        conn.execute(text("DELETE FROM users"))
    engine.dispose()


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


def unique_id() -> str:
    return uuid.uuid4().hex[:10]
