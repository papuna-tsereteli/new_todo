# back/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
import models

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# The connect_args is crucial for SQLite in-memory to be shared across threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture-based Setup ---

@pytest.fixture()
def client():
    """
    A fixture that sets up the database, provides a test client, and cleans up.
    This is the modern and correct way to handle test databases.
    """
    # Create the tables in the database
    models.Base.metadata.create_all(bind=engine)

    def override_get_db():
        """A dependency override that provides a test database session."""
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Apply the override to the app
    app.dependency_overrides[get_db] = override_get_db

    # Yield the TestClient for the test to use
    yield TestClient(app)

    # Teardown: drop all tables after the test is done to ensure isolation
    models.Base.metadata.drop_all(bind=engine)