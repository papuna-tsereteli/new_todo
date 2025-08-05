# back/conftest.py
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Enable testing mode before any imports
os.environ["TESTING"] = "true"
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def override_get_db():
    from database import SessionLocal
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(monkeypatch):
    # Mock reindex
    monkeypatch.setattr("reindex.reindex_all_todos", lambda: None)

    import models
    from database import Base, engine
    from main import app, get_db

    # Override DB dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create tables once per test
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # Drop tables after test
    Base.metadata.drop_all(bind=engine)
