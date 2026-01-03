"""Integration test for conversation lifecycle with PostgreSQL.

NOTE: These tests are currently skipped pending testcontainers infrastructure setup.

These integration tests validate:
- User authentication flow
- Conversation creation and persistence
- Message creation and persistence
- Cascade deletion (conversation + messages)
- User ownership enforcement

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

TODO (Phase 3.1 - Testing Infrastructure):
- Add testcontainers-python for real PostgreSQL testing
- Migrate to pytest-anyio (FastAPI 2025 standard)
- Create proper integration test fixtures
- Re-enable these tests

Current Issues:
- bcrypt backend initialization conflicts
- Database session management with async event loops
- Need PostgreSQL testcontainers instead of production database

Plan: Dedicated testing infrastructure session to properly implement:
1. testcontainers-python with PostgreSQL 16
2. pytest-anyio migration from pytest-asyncio
3. Proper async database session fixtures
4. Transaction rollback patterns for test isolation
"""

import pytest

# Skip all integration tests until testcontainers infrastructure is ready
pytestmark = pytest.mark.skip(
    reason="Integration test infrastructure pending - requires testcontainers setup (Phase 3.1)"
)
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.dependencies import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User


@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_lifecycle_create_add_message_delete_cascades():
    """Test complete conversation lifecycle: create, add message, delete, verify cascade.

    This end-to-end test validates:
    1. User registration and authentication
    2. Conversation creation
    3. Message creation and persistence
    4. Cascade deletion (deleting conversation removes messages)
    5. Database persistence with PostgreSQL
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Register a test user
        register_response = await client.post(
            "/api/auth/register",
            json={"email": "test_lifecycle@example.com", "password": "testpass123"}
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        user_id = user_data["id"]

        # Step 2: Login to get JWT token
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "test_lifecycle@example.com", "password": "testpass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Create a conversation
        create_conv_response = await client.post(
            "/api/conversations",
            json={"title": "Test Conversation", "current_mode": "balanced"},
            headers=headers
        )
        assert create_conv_response.status_code == 201
        conversation_data = create_conv_response.json()
        conversation_id = conversation_data["id"]
        assert conversation_data["title"] == "Test Conversation"
        assert conversation_data["current_mode"] == "balanced"
        assert conversation_data["user_id"] == user_id

        # Step 4: Add a message to the conversation
        add_message_response = await client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"role": "user", "content": "Hello, this is a test message"},
            headers=headers
        )
        assert add_message_response.status_code == 201
        message_data = add_message_response.json()
        message_id = message_data["id"]
        assert message_data["role"] == "user"
        assert message_data["content"] == "Hello, this is a test message"
        assert message_data["conversation_id"] == conversation_id

        # Step 5: Verify conversation and message exist in database
        async for db in get_db():
            # Verify conversation exists
            conv_result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = conv_result.scalar_one_or_none()
            assert conversation is not None
            assert conversation.title == "Test Conversation"

            # Verify message exists
            msg_result = await db.execute(
                select(Message).where(Message.id == message_id)
            )
            message = msg_result.scalar_one_or_none()
            assert message is not None
            assert message.content == "Hello, this is a test message"
            assert message.conversation_id == conversation_id
            break  # Exit after first iteration

        # Step 6: Delete the conversation
        delete_response = await client.delete(
            f"/api/conversations/{conversation_id}",
            headers=headers
        )
        assert delete_response.status_code == 204

        # Step 7: Verify conversation and message are deleted (cascade)
        async for db in get_db():
            # Verify conversation is gone
            conv_result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = conv_result.scalar_one_or_none()
            assert conversation is None

            # Verify message is also gone (cascade delete)
            msg_result = await db.execute(
                select(Message).where(Message.id == message_id)
            )
            message = msg_result.scalar_one_or_none()
            assert message is None
            break  # Exit after first iteration


@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_list_returns_only_user_conversations():
    """Test that users can only see their own conversations (ownership enforcement)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create two users
        user1_response = await client.post(
            "/api/auth/register",
            json={"email": "user1_ownership@example.com", "password": "testpass123"}
        )
        assert user1_response.status_code == 201

        user2_response = await client.post(
            "/api/auth/register",
            json={"email": "user2_ownership@example.com", "password": "testpass123"}
        )
        assert user2_response.status_code == 201

        # Login as user1
        user1_login = await client.post(
            "/api/auth/login",
            data={"username": "user1_ownership@example.com", "password": "testpass123"}
        )
        user1_token = user1_login.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        # Login as user2
        user2_login = await client.post(
            "/api/auth/login",
            data={"username": "user2_ownership@example.com", "password": "testpass123"}
        )
        user2_token = user2_login.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # User1 creates a conversation
        user1_conv = await client.post(
            "/api/conversations",
            json={"title": "User 1 Conversation"},
            headers=user1_headers
        )
        assert user1_conv.status_code == 201
        user1_conv_id = user1_conv.json()["id"]

        # User2 creates a conversation
        user2_conv = await client.post(
            "/api/conversations",
            json={"title": "User 2 Conversation"},
            headers=user2_headers
        )
        assert user2_conv.status_code == 201

        # User1 lists conversations - should only see their own
        user1_list = await client.get("/api/conversations", headers=user1_headers)
        assert user1_list.status_code == 200
        user1_conversations = user1_list.json()
        assert len(user1_conversations) == 1
        assert user1_conversations[0]["title"] == "User 1 Conversation"

        # User2 tries to access User1's conversation - should get 404
        user2_access = await client.get(
            f"/api/conversations/{user1_conv_id}",
            headers=user2_headers
        )
        assert user2_access.status_code == 404
        assert "not found" in user2_access.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_get_includes_messages():
    """Test that getting a conversation includes all its messages."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post(
            "/api/auth/register",
            json={"email": "test_messages@example.com", "password": "testpass123"}
        )
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "test_messages@example.com", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conv_response = await client.post(
            "/api/conversations",
            json={"title": "Test with Messages"},
            headers=headers
        )
        conversation_id = conv_response.json()["id"]

        # Add multiple messages
        await client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"role": "user", "content": "First message"},
            headers=headers
        )
        await client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"role": "assistant", "content": "Response message"},
            headers=headers
        )
        await client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"role": "user", "content": "Follow-up message"},
            headers=headers
        )

        # Get conversation with messages
        get_response = await client.get(
            f"/api/conversations/{conversation_id}",
            headers=headers
        )
        assert get_response.status_code == 200
        data = get_response.json()

        # Verify messages are included
        assert "messages" in data
        assert len(data["messages"]) == 3
        assert data["messages"][0]["content"] == "First message"
        assert data["messages"][1]["content"] == "Response message"
        assert data["messages"][2]["content"] == "Follow-up message"
