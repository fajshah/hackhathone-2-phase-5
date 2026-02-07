import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from src.main import app
from src.models.task import Task, TaskStatus, TaskPriority
from src.services.task_service import TaskService


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.integration
class TestTaskAPI:
    """Integration tests for the Task API endpoints."""

    def test_create_task_endpoint(self, client):
        """Test creating a task through the API endpoint."""
        # Arrange
        task_data = {
            "title": "Integration Test Task",
            "description": "A task created via API integration test",
            "user_id": "user123",
            "priority": "high"
        }

        # Act
        response = client.post("/api/v1/tasks", json=task_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert "id" in response_data
        assert response_data["title"] == "Integration Test Task"
        assert response_data["description"] == "A task created via API integration test"
        assert response_data["status"] == "pending"
        assert response_data["user_id"] == "user123"
        assert response_data["priority"] == "high"

    def test_get_tasks_endpoint(self, client):
        """Test getting tasks through the API endpoint."""
        # Arrange - Create a task first
        task_data = {
            "title": "Get Tasks Test",
            "description": "Test task for get tasks endpoint",
            "user_id": "user123"
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Act - Get tasks
        response = client.get("/api/v1/tasks?user_id=user123")

        # Assert
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1

        # Find the test task in the response
        test_task = next((t for t in tasks if t["id"] == task_id), None)
        assert test_task is not None
        assert test_task["title"] == "Get Tasks Test"

    def test_get_specific_task_endpoint(self, client):
        """Test getting a specific task through the API endpoint."""
        # Arrange - Create a task first
        task_data = {
            "title": "Get Specific Task Test",
            "description": "Test task for getting specific task",
            "user_id": "user123"
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Act - Get specific task
        response = client.get(f"/api/v1/tasks/{task_id}?user_id=user123")

        # Assert
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == "Get Specific Task Test"

    def test_update_task_endpoint(self, client):
        """Test updating a task through the API endpoint."""
        # Arrange - Create a task first
        task_data = {
            "title": "Original Task Title",
            "description": "Original description",
            "user_id": "user123"
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Prepare update data
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "status": "completed"
        }

        # Act - Update task
        response = client.put(f"/api/v1/tasks/{task_id}?user_id=user123", json=update_data)

        # Assert
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Updated Task Title"
        assert updated_task["description"] == "Updated description"
        assert updated_task["status"] == "completed"

    def test_complete_task_endpoint(self, client):
        """Test completing a task through the API endpoint."""
        # Arrange - Create a task first
        task_data = {
            "title": "Task to Complete",
            "description": "Test task for completion endpoint",
            "user_id": "user123"
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Act - Complete task
        response = client.post(f"/api/v1/tasks/{task_id}/complete?user_id=user123")

        # Assert
        assert response.status_code == 200
        completed_task = response.json()
        assert completed_task["id"] == task_id
        assert completed_task["status"] == "completed"

    def test_delete_task_endpoint(self, client):
        """Test deleting a task through the API endpoint."""
        # Arrange - Create a task first
        task_data = {
            "title": "Task to Delete",
            "description": "Test task for deletion endpoint",
            "user_id": "user123"
        }

        create_response = client.post("/api/v1/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Act - Delete task
        response = client.delete(f"/api/v1/tasks/{task_id}?user_id=user123")

        # Assert
        assert response.status_code == 204

        # Verify task no longer exists
        get_response = client.get(f"/api/v1/tasks/{task_id}?user_id=user123")
        assert get_response.status_code == 404

    def test_invalid_task_data_returns_error(self, client):
        """Test that invalid task data returns appropriate error."""
        # Arrange - Invalid task data (no title)
        invalid_task_data = {
            "description": "Task without title",
            "user_id": "user123"
        }

        # Act
        response = client.post("/api/v1/tasks", json=invalid_task_data)

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert "detail" in response_data

    def test_nonexistent_task_returns_error(self, client):
        """Test that requesting a nonexistent task returns appropriate error."""
        # Act
        response = client.get("/api/v1/tasks/nonexistent-task-id?user_id=user123")

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data


@pytest.mark.integration
class TestHealthAPI:
    """Integration tests for the Health API endpoints."""

    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "healthy"

    def test_health_v1_endpoint(self, client):
        """Test the health endpoint under API version."""
        # Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "status" in response_data
        assert response_data["status"] == "healthy"


@pytest.mark.integration
class TestChatAPI:
    """Integration tests for the Chat API endpoints."""

    def test_chat_endpoint_basic_response(self, client):
        """Test the chat endpoint with a basic message."""
        # Arrange
        chat_data = {
            "message": "Create a task to buy groceries",
            "user_id": "user123"
        }

        # Act
        response = client.post("/api/v1/chat", json=chat_data)

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "response" in response_data
        assert "actions" in response_data
        assert isinstance(response_data["actions"], list)

    def test_chat_endpoint_empty_message(self, client):
        """Test the chat endpoint with an empty message."""
        # Arrange
        chat_data = {
            "message": "",
            "user_id": "user123"
        }

        # Act
        response = client.post("/api/v1/chat", json=chat_data)

        # Assert
        # The response should be 200 but with an error message or guidance
        assert response.status_code == 200
        response_data = response.json()
        assert "response" in response_data