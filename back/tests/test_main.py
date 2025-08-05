# back/tests/test_main.py

from unittest.mock import patch, MagicMock, AsyncMock


# The client fixture will be injected by pytest from conftest.py
def test_create_todo(client):
    """
    Test creating a new to-do item.
    """
    response = client.post("/todos/", json={"text": "Test Todo", "completed": False})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Test Todo"
    assert "id" in data


def test_read_todos(client):
    """
    Test reading all to-do items.
    """
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
    create_response = client.post("/todos/", json={"text": "Todo to update", "completed": False})
    todo_id = create_response.json()["id"]

    update_response = client.put(f"/todos/{todo_id}", json={"text": "Updated Text", "completed": True})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["text"] == "Updated Text"
    assert data["completed"] is True


def test_delete_todo(client):
    """
    Test deleting a to-do item.
    """
    create_response = client.post("/todos/", json={"text": "Todo to delete", "completed": False})
    todo_id = create_response.json()["id"]

    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 200

    read_response = client.get(f"/todos/{todo_id}")
    assert read_response.status_code == 404


def test_search_todos(client):
    """
    Test the vector search functionality with mocked results.
    """
    # Create a mock search result
    mock_search_result = MagicMock()
    mock_search_result.id = 1
    mock_search_result.score = 0.85
    mock_search_result.payload = {"text": "Buy groceries"}

    with patch('main.vector_db_client') as mock_vector_db:
        mock_vector_db.search_todos.return_value = [mock_search_result]

        response = client.post("/todos/search", json={"query": "shopping"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == 1
        assert data["results"][0]["text"] == "Buy groceries"
        assert data["results"][0]["score"] == 0.85


def test_search_todos_with_low_scores_filtered(client):
    """
    Test that search results with low confidence scores are filtered out.
    """
    # Create mock search results with different scores
    high_score_result = MagicMock()
    high_score_result.id = 1
    high_score_result.score = 0.85
    high_score_result.payload = {"text": "High confidence match"}

    low_score_result = MagicMock()
    low_score_result.id = 2
    low_score_result.score = 0.15  # Below the 0.30 threshold
    low_score_result.payload = {"text": "Low confidence match"}

    with patch('main.vector_db_client') as mock_vector_db:
        mock_vector_db.search_todos.return_value = [high_score_result, low_score_result]

        response = client.post("/todos/search", json={"query": "test"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1  # Only high confidence result
        assert data["results"][0]["score"] == 0.85


def test_search_todos_empty_results(client):
    """
    Test search endpoint when no results are found.
    """
    with patch('main.vector_db_client') as mock_vector_db:
        mock_vector_db.search_todos.return_value = []

        response = client.post("/todos/search", json={"query": "nonexistent"})
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []


# --- Mocked AI Suggestion Test ---

@patch('main.get_suggestions_graph')
def test_suggest_todos_mocked(mock_get_graph, client):
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


@patch('main.get_suggestions_graph')
def test_suggest_todos_error_handling(mock_get_graph, client):
    """
    Tests error handling in the AI suggestion endpoint.
    """
    mock_graph_instance = MagicMock()
    mock_graph_instance.ainvoke = AsyncMock(side_effect=Exception("AI service unavailable"))
    mock_get_graph.return_value = mock_graph_instance

    response = client.post(
        "/todos/suggest",
        json={"tasks": ["Plan my next project"]}
    )

    assert response.status_code == 500
    assert "Failed to generate AI suggestions" in response.json()["detail"]