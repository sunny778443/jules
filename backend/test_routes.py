import pytest
import json
import os
from database import get_db, Base
import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

if os.path.exists("test.db"):
    try:
        os.remove("test.db")
    except Exception:
        pass

test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

database.engine = test_engine
database.SessionLocal = TestingSessionLocal

import models
Base.metadata.create_all(bind=test_engine)

from main import app
from fastapi.testclient import TestClient

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_sessions_lifecycle():
    resp = client.post("/api/sessions")
    assert resp.status_code == 200
    session_id = resp.json()["id"]
    assert session_id is not None

    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == session_id
    assert len(resp.json()["messages"]) == 0

    resp = client.post(f"/api/sessions/{session_id}/messages", json={"content": "What is the weather like?"})
    assert resp.status_code == 200
    ai_resp = resp.json()
    assert ai_resp["sender"] == "ai"
    assert "weather" in ai_resp["content"].lower()

    resp = client.get("/api/memories")
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    resp = client.get("/api/plugins")
    assert resp.status_code == 200
    plugins = resp.json()
    assert any(p["id"] == "weather" for p in plugins)

    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except Exception:
            pass
