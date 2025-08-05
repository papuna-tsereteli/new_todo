# back/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app, get_db
import models

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the table before tests run
models.Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    A dependency override that provides a test database session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# This line tells our app to use the test database instead of the real one
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def client():
    """
    Provides a TestClient instance for making requests to the FastAPI app.
    """
    yield TestClient(app)