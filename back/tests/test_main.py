# back/test_main.py

from unittest.mock import patch, MagicMock, AsyncMock

# No need to import TestClient, create_engine, sessionmaker, or Base here
# conftest.py handles all of that.

# The client fixture will be injected by pytest from conftest.py
def test_create_todo(client):
    """
    Test creating a new to-do item.
    """
    # Mock the vector DB client to prevent actual network calls during unit tests
    with patch('back.main.vector_db_client') as mock_vector_db:
        response = client.post("/todos/", json={"text": "Test Todo", "completed": False})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test Todo"
        assert "id" in data
        # Assert that the vector DB was called
        mock_vector_db.upsert_todo.assert_called_once()


def test_read_todos(client):
    """
    Test reading all to-do items.
    """
    # Create an item to ensure the list is not empty
    with patch('back.main.vector_db_client'):
        client.post("/todos/", json={"text": "Another Test Todo", "completed": False})

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_todo(client):
    """
    Test updating an existing to-do item.
    """
    with patch('back.main.vector_db_client') as mock_vector_db:
        create_response = client.post("/todos/", json={"text": "Todo to update", "completed": False})
        todo_id = create_response.json()["id"]

        update_response = client.put(f"/todos/{todo_id}", json={"text": "Updated Text", "completed": True})
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["text"] == "Updated Text"
        assert data["completed"] is True
        # Assert that the vector DB was updated
        mock_vector_db.upsert_todo.assert_called_with(todo_id=todo_id, todo_text="Updated Text")


def test_delete_todo(client):
    """
    Test deleting a to-do item.
    """
    with patch('back.main.vector_db_client') as mock_vector_db:
        create_response = client.post("/todos/", json={"text": "Todo to delete", "completed": False})
        todo_id = create_response.json()["id"]

        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 200

        # Assert that the vector was deleted
        mock_vector_db.delete_todo_vector.assert_called_with(todo_id=todo_id)

        read_response = client.get(f"/todos/{todo_id}")
        assert read_response.status_code == 404


# --- Mocked AI Suggestion Test ---

@patch('back.main.get_suggestions_graph')
def test_suggest_todos_mocked(mock_get_graph, client): # Add client fixture here
    """
    Tests the AI suggestion endpoint by mocking the LangGraph call.
    """
    mock_graph_instance = MagicMock()
    mock_graph_instance.ainvoke = AsyncMock(return_value={
        "suggestions": ["Mocked Suggestion 1", "Mocked Suggestion 2"]
    })
    mock_get_graph.return_value = mock_graph_instance

    response = client.post(
        "/todos/suggest",
        json={"tasks": ["Plan my next project"]}
    )

    assert response.status_code == 200
    assert response.json() == {
        "suggestions": ["Mocked Suggestion 1", "Mocked Suggestion 2"]
    }