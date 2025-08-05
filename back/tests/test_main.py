import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Import your FastAPI app and database configuration
from back.main import app, get_db
from back.database import Base

# --- Test Database Setup ---
# Use an in-memory SQLite database for testing. It's fast and self-contained.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database before tests run
Base.metadata.create_all(bind=engine)


# --- Dependency Override ---
# This is a key part of FastAPI testing.
# We override the `get_db` dependency to use our temporary test database
# instead of the real PostgreSQL one.
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create a TestClient instance
client = TestClient(app)


# --- Standard CRUD Tests ---

def test_create_todo():
    """
    Tests creating a new to-do item via the POST /todos/ endpoint.
    """
    response = client.post("/todos/", json={"text": "Test Todo", "completed": False})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Test Todo"
    assert data["completed"] is False
    assert "id" in data


def test_read_todos():
    """
    Tests fetching all to-do items from the GET /todos/ endpoint.
    """
    # Create an item first to ensure the database isn't empty
    client.post("/todos/", json={"text": "Another Test Todo"})
    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[-1]["text"] == "Another Test Todo"


def test_update_todo():
    """
    Tests updating an existing to-do item via the PUT /todos/{todo_id} endpoint.
    """
    # 1. Create a todo
    response_create = client.post("/todos/", json={"text": "Todo to update"})
    assert response_create.status_code == 200
    todo_id = response_create.json()["id"]

    # 2. Update the todo
    response_update = client.put(
        f"/todos/{todo_id}",
        json={"text": "Updated Text", "completed": True}
    )
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["text"] == "Updated Text"
    assert data["completed"] is True


def test_delete_todo():
    """
    Tests deleting a to-do item and ensuring it's gone.
    """
    # 1. Create a todo
    response_create = client.post("/todos/", json={"text": "Todo to delete"})
    assert response_create.status_code == 200
    todo_id = response_create.json()["id"]

    # 2. Delete the todo
    response_delete = client.delete(f"/todos/{todo_id}")
    assert response_delete.status_code == 200

    # 3. Verify it's gone (should return a 404 Not Found)
    response_get = client.get(f"/todos/{todo_id}")
    assert response_get.status_code == 404


# --- Mocked AI Suggestion Test ---

# The `@patch` decorator intercepts the call to `main.get_suggestions_graph`.
# Instead of running the real function, it passes a mock object into our test.
@patch('back.main.get_suggestions_graph')
def test_suggest_todos_mocked(mock_get_graph):
    """
    Tests the AI suggestion endpoint by mocking the LangGraph call.
    """
    # Configure the mock object to behave like the real graph
    mock_graph_instance = MagicMock()

    # Use AsyncMock to define the return value of the awaitable method
    mock_graph_instance.ainvoke = AsyncMock(return_value={
        "suggestions": ["Mocked Suggestion 1", "Mocked Suggestion 2"]
    })

    mock_get_graph.return_value = mock_graph_instance

    # The rest of the test code remains the same
    response = client.post(
        "/todos/suggest",
        json={"tasks": ["Plan my next project"]}
    )

    assert response.status_code == 200
    assert response.json() == {
        "suggestions": ["Mocked Suggestion 1", "Mocked Suggestion 2"]
    }