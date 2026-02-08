import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from src.services.task_service import TaskService
from src.models.task import Task, TaskStatus, TaskPriority
from src.services.task_repository import TaskRepository


@pytest.fixture
def mock_repository():
    """Create a mock task repository for testing."""
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def task_service(mock_repository):
    """Create a task service instance with a mock repository."""
    return TaskService(task_repository=mock_repository)


@pytest.mark.asyncio
class TestTaskService:
    """Unit tests for the TaskService class."""

    async def test_create_task_success(self, task_service, mock_repository):
        """Test successful task creation."""
        # Arrange
        task_data = {
            "title": "Test Task",
            "description": "A test task",
            "user_id": "user123",
            "status": TaskStatus.PENDING,
            "priority": TaskPriority.MEDIUM,
            "due_date": datetime(2024, 12, 31)
        }

        expected_task = Task(
            id="test-id",
            title="Test Task",
            description="A test task",
            user_id="user123",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=datetime(2024, 12, 31)
        )

        mock_repository.create_task.return_value = expected_task

        # Act
        result = await task_service.create_task(task_data)

        # Assert
        assert result == expected_task
        mock_repository.create_task.assert_called_once()

        # Verify the call arguments
        call_args = mock_repository.create_task.call_args[0][0]  # First positional arg of the call
        assert call_args["title"] == "Test Task"
        assert call_args["description"] == "A test task"
        assert call_args["user_id"] == "user123"

    async def test_get_task_by_id_success(self, task_service, mock_repository):
        """Test getting a task by ID."""
        # Arrange
        task_id = "task123"
        user_id = "user123"

        expected_task = Task(
            id=task_id,
            title="Test Task",
            user_id=user_id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = expected_task

        # Act
        result = await task_service.get_task_by_id(task_id, user_id)

        # Assert
        assert result == expected_task
        mock_repository.get_task_by_id.assert_called_once_with(task_id)

    async def test_get_task_by_id_wrong_user(self, task_service, mock_repository):
        """Test getting a task by ID when the user doesn't own the task."""
        # Arrange
        task_id = "task123"
        user_id = "user123"
        other_user_id = "user456"

        existing_task = Task(
            id=task_id,
            title="Test Task",
            user_id=other_user_id,  # Different user
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task

        # Act
        result = await task_service.get_task_by_id(task_id, user_id)

        # Assert
        assert result is None
        mock_repository.get_task_by_id.assert_called_once_with(task_id)

    async def test_get_tasks_for_user_success(self, task_service, mock_repository):
        """Test getting tasks for a user."""
        # Arrange
        user_id = "user123"
        tasks = [
            Task(id="task1", title="Task 1", user_id=user_id, status=TaskStatus.PENDING, priority=TaskPriority.MEDIUM),
            Task(id="task2", title="Task 2", user_id=user_id, status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH)
        ]

        mock_repository.get_tasks_by_user.return_value = tasks

        # Act
        result = await task_service.get_tasks_for_user(user_id)

        # Assert
        assert result == tasks
        mock_repository.get_tasks_by_user.assert_called_once_with(user_id, None, 20, 0)

    async def test_update_task_success(self, task_service, mock_repository):
        """Test updating a task successfully."""
        # Arrange
        task_id = "task123"
        user_id = "user123"
        update_data = {"title": "Updated Task", "status": TaskStatus.COMPLETED}

        existing_task = Task(
            id=task_id,
            title="Original Task",
            user_id=user_id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        updated_task = Task(
            id=task_id,
            title="Updated Task",
            user_id=user_id,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task
        mock_repository.update_task.return_value = updated_task

        # Act
        result = await task_service.update_task(task_id, user_id, update_data)

        # Assert
        assert result == updated_task
        mock_repository.update_task.assert_called_once()

    async def test_update_task_wrong_user(self, task_service, mock_repository):
        """Test updating a task when the user doesn't own it."""
        # Arrange
        task_id = "task123"
        user_id = "user123"
        other_user_id = "user456"
        update_data = {"title": "Updated Task"}

        existing_task = Task(
            id=task_id,
            title="Original Task",
            user_id=other_user_id,  # Different user
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task

        # Act
        result = await task_service.update_task(task_id, user_id, update_data)

        # Assert
        assert result is None
        mock_repository.update_task.assert_not_called()

    async def test_complete_task_success(self, task_service, mock_repository):
        """Test completing a task successfully."""
        # Arrange
        task_id = "task123"
        user_id = "user123"

        existing_task = Task(
            id=task_id,
            title="Original Task",
            user_id=user_id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        completed_task = Task(
            id=task_id,
            title="Original Task",
            user_id=user_id,
            status=TaskStatus.COMPLETED,  # Status changed
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task
        mock_repository.complete_task.return_value = completed_task

        # Act
        result = await task_service.complete_task(task_id, user_id)

        # Assert
        assert result == completed_task
        mock_repository.complete_task.assert_called_once_with(task_id)

    async def test_complete_task_wrong_user(self, task_service, mock_repository):
        """Test completing a task when the user doesn't own it."""
        # Arrange
        task_id = "task123"
        user_id = "user123"
        other_user_id = "user456"

        existing_task = Task(
            id=task_id,
            title="Original Task",
            user_id=other_user_id,  # Different user
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task

        # Act
        result = await task_service.complete_task(task_id, user_id)

        # Assert
        assert result is None
        mock_repository.complete_task.assert_not_called()

    async def test_delete_task_success(self, task_service, mock_repository):
        """Test deleting a task successfully."""
        # Arrange
        task_id = "task123"
        user_id = "user123"

        existing_task = Task(
            id=task_id,
            title="Task to delete",
            user_id=user_id,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task
        mock_repository.delete_task.return_value = True

        # Act
        result = await task_service.delete_task(task_id, user_id)

        # Assert
        assert result is True
        mock_repository.delete_task.assert_called_once_with(task_id)

    async def test_delete_task_wrong_user(self, task_service, mock_repository):
        """Test deleting a task when the user doesn't own it."""
        # Arrange
        task_id = "task123"
        user_id = "user123"
        other_user_id = "user456"

        existing_task = Task(
            id=task_id,
            title="Task to delete",
            user_id=other_user_id,  # Different user
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )

        mock_repository.get_task_by_id.return_value = existing_task

        # Act
        result = await task_service.delete_task(task_id, user_id)

        # Assert
        assert result is False
        mock_repository.delete_task.assert_not_called()

    async def test_validate_task_data_valid(self, task_service):
        """Test validating valid task data."""
        # Arrange
        valid_data = {
            "title": "Valid Task",
            "description": "A valid task description",
            "status": "pending",
            "priority": "high",
            "user_id": "user123"
        }

        # Act & Assert
        # Should not raise an exception
        await task_service._validate_task_data(valid_data)

    async def test_validate_task_data_invalid_title(self, task_service):
        """Test validating task data with invalid title."""
        # Arrange
        invalid_data = {
            "title": "",  # Empty title
            "user_id": "user123"
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Title is required"):
            await task_service._validate_task_data(invalid_data)

    async def test_validate_task_data_long_title(self, task_service):
        """Test validating task data with too long title."""
        # Arrange
        invalid_data = {
            "title": "a" * 256,  # Too long title
            "user_id": "user123"
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Title is required"):
            await task_service._validate_task_data(invalid_data)

    async def test_validate_task_data_invalid_status(self, task_service):
        """Test validating task data with invalid status."""
        # Arrange
        invalid_data = {
            "title": "Valid Task",
            "status": "invalid_status",
            "user_id": "user123"
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid status"):
            await task_service._validate_task_data(invalid_data)

    async def test_validate_task_data_invalid_priority(self, task_service):
        """Test validating task data with invalid priority."""
        # Arrange
        invalid_data = {
            "title": "Valid Task",
            "priority": "invalid_priority",
            "user_id": "user123"
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid priority"):
            await task_service._validate_task_data(invalid_data)

    async def test_task_status_transition_validation(self, task_service):
        """Test task status transition validation."""
        # Arrange
        pending_status = TaskStatus.PENDING
        in_progress_status = TaskStatus.IN_PROGRESS
        completed_status = TaskStatus.COMPLETED

        # Act & Assert - Valid transitions
        assert task_service._validate_task_transition(pending_status, in_progress_status)
        assert task_service._validate_task_transition(in_progress_status, completed_status)
        assert task_service._validate_task_transition(completed_status, pending_status)  # Explicit reopening allowed

        # Invalid transition (for this implementation)
        # Note: Our current implementation allows most transitions, but you could customize this
        # For example, if we had strict state machine logic:
        # assert not task_service._validate_task_transition(completed_status, in_progress_status)