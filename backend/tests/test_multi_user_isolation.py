"""
Test suite for multi-user support and data isolation in the Todo AI Chatbot.
This covers tasks T045-T052 from the implementation plan.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from sqlmodel import SQLModel, create_engine, Session, delete
from backend.src.models.task import Task
from backend.src.models.user import User
from backend.src.models.conversation import Conversation
from backend.src.services.task_service import TaskService
from backend.src.services.conversation_service import ConversationService


@pytest.fixture
def setup_test_db():
    """Set up a test database session."""
    engine = create_engine("sqlite:///:memory:", echo=True)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.mark.asyncio
async def test_user_data_isolation_for_tasks(setup_test_db):
    """
    Test T050: Test data isolation between multiple users
    Given: Two different users are using the system
    When: They both create tasks
    Then: Each user only sees their own tasks
    """
    session = setup_test_db

    # Create two different users
    user1 = User(email="user1@example.com", auth_data="mock_auth_data")
    user2 = User(email="user2@example.com", auth_data="mock_auth_data")

    session.add(user1)
    session.add(user2)
    session.commit()

    session.refresh(user1)
    session.refresh(user2)

    # User 1 creates tasks
    task_service = TaskService()
    from backend.src.models.task import TaskCreate

    task_create_1 = TaskCreate(title="User 1 task 1", user_id=user1.id, description="Task for user 1")
    task_create_2 = TaskCreate(title="User 1 task 2", user_id=user1.id, description="Another task for user 1")

    task1_user1 = TaskService.create_task(session, task_create_1, user1)
    task2_user1 = TaskService.create_task(session, task_create_2, user1)

    # User 2 creates tasks
    task_create_3 = TaskCreate(title="User 2 task 1", user_id=user2.id, description="Task for user 2")
    task_create_4 = TaskCreate(title="User 2 task 2", user_id=user2.id, description="Another task for user 2")

    task1_user2 = TaskService.create_task(session, task_create_3, user2)
    task2_user2 = TaskService.create_task(session, task_create_4, user2)

    # Verify User 1 only sees their own tasks
    user1_tasks = TaskService.get_tasks_by_user(session, user1)
    assert len(user1_tasks) == 2
    for task in user1_tasks:
        assert task.user_id == user1.id
        assert task.title in ["User 1 task 1", "User 1 task 2"]

    # Verify User 2 only sees their own tasks
    user2_tasks = TaskService.get_tasks_by_user(session, user2)
    assert len(user2_tasks) == 2
    for task in user2_tasks:
        assert task.user_id == user2.id
        assert task.title in ["User 2 task 1", "User 2 task 2"]

    # Verify no cross-contamination
    user1_task_titles = [task.title for task in user1_tasks]
    user2_task_titles = [task.title for task in user2_tasks]

    assert "User 1 task 1" not in user2_task_titles
    assert "User 1 task 2" not in user2_task_titles
    assert "User 2 task 1" not in user1_task_titles
    assert "User 2 task 2" not in user1_task_titles


@pytest.mark.asyncio
async def test_user_specific_task_access_controls(setup_test_db):
    """
    Test T051: Test user-specific task access controls
    Given: User A has tasks and User B tries to access them
    When: User B attempts to perform operations on User A's tasks
    Then: Access is denied and User B cannot see or modify User A's tasks
    """
    session = setup_test_db

    # Create two different users
    user_a = User(email="user_a@example.com", auth_data="mock_auth_data")
    user_b = User(email="user_b@example.com", auth_data="mock_auth_data")

    session.add(user_a)
    session.add(user_b)
    session.commit()

    session.refresh(user_a)
    session.refresh(user_b)

    # User A creates a task
    from backend.src.models.task import TaskCreate
    task_create = TaskCreate(title="User A's private task", user_id=user_a.id, description="Private to User A")
    user_a_task = TaskService.create_task(session, task_create, user_a)

    assert user_a_task is not None
    assert user_a_task.user_id == user_a.id

    # Attempt to access User A's task as User B using the service layer
    # This should return None or raise an exception
    from backend.src.models.task import TaskUpdate

    # Try to update User A's task as User B (should fail)
    task_update = TaskUpdate(title="Modified by User B")
    updated_task = TaskService.update_task(session, user_a_task.id, task_update, user_b)
    assert updated_task is None  # Should return None due to authorization failure

    # Try to get User A's task as User B (should return None)
    retrieved_task = TaskService.get_task_by_id(session, user_a_task.id, user_b)
    assert retrieved_task is None  # Should return None due to authorization failure

    # Try to delete User A's task as User B (should fail)
    delete_result = TaskService.delete_task(session, user_a_task.id, user_b)
    assert delete_result is False  # Should return False due to authorization failure

    # Verify the task still exists and belongs to User A
    task_still_exists = TaskService.get_task_by_id(session, user_a_task.id, user_a)
    assert task_still_exists is not None
    assert task_still_exists.id == user_a_task.id
    assert task_still_exists.user_id == user_a.id


@pytest.mark.asyncio
async def test_user_specific_conversation_access_controls(setup_test_db):
    """
    Test T052: Test user-specific conversation access controls
    Given: User A has conversations and User B tries to access them
    When: User B attempts to access User A's conversations
    Then: Access is denied and User B cannot see User A's conversations
    """
    session = setup_test_db

    # Create two different users
    user_a = User(email="user_a@example.com", auth_data="mock_auth_data")
    user_b = User(email="user_b@example.com", auth_data="mock_auth_data")

    session.add(user_a)
    session.add(user_b)
    session.commit()

    session.refresh(user_a)
    session.refresh(user_b)

    # User A creates a conversation
    from backend.src.models.conversation import ConversationCreate
    conversation_create = ConversationCreate(
        title="User A's private conversation",
        description="Private to User A",
        user_id=user_a.id
    )
    user_a_conversation = ConversationService.create_conversation(session, conversation_create, user_a)

    assert user_a_conversation is not None
    assert user_a_conversation.user_id == user_a.id

    # Attempt to access User A's conversation as User B
    # This should return None or raise an exception
    retrieved_conversation = ConversationService.get_conversation_by_id(
        session,
        user_a_conversation.id,
        user_b
    )
    assert retrieved_conversation is None  # Should return None due to authorization failure

    # Verify User A can still access their own conversation
    own_conversation = ConversationService.get_conversation_by_id(
        session,
        user_a_conversation.id,
        user_a
    )
    assert own_conversation is not None
    assert own_conversation.id == user_a_conversation.id
    assert own_conversation.user_id == user_a.id

    # Verify that each user only sees their own conversations when getting all conversations
    user_a_conversations = ConversationService.get_conversations_by_user(session, user_a)
    user_b_conversations = ConversationService.get_conversations_by_user(session, user_b)

    assert len(user_a_conversations) == 1
    assert len(user_b_conversations) == 0  # User B has no conversations yet

    # Create a conversation for User B
    conversation_create_b = ConversationCreate(
        title="User B's conversation",
        description="Owned by User B",
        user_id=user_b.id
    )
    user_b_conversation = ConversationService.create_conversation(session, conversation_create_b, user_b)

    # Verify data isolation remains intact
    user_a_conversations_after = ConversationService.get_conversations_by_user(session, user_a)
    user_b_conversations_after = ConversationService.get_conversations_by_user(session, user_b)

    assert len(user_a_conversations_after) == 1  # Still only User A's original conversation
    assert len(user_b_conversations_after) == 1  # Now has User B's conversation
    assert user_a_conversations_after[0].id == user_a_conversation.id
    assert user_b_conversations_after[0].id == user_b_conversation.id


if __name__ == "__main__":
    pytest.main([__file__])