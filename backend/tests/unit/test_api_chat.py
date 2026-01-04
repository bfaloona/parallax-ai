"""Unit tests for chat endpoint.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

Example:
    test_chat_endpoint_valid_message_returns_200()
"""

import pytest
from httpx import AsyncClient
from typing import AsyncGenerator, Dict
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

from app.main import app
from app.dependencies import get_current_user, get_db
from app.services.conversation_service import ConversationService
from app.models.conversation import Conversation, Message as MessageModel


@pytest.fixture
def mock_user_id():
    """Mock user ID for tests."""
    return uuid4()


@pytest.fixture
def mock_conversation_id():
    """Mock conversation ID for tests."""
    return uuid4()


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_conversation(mock_user_id, mock_conversation_id):
    """Mock conversation with messages."""
    conversation = Conversation(
        id=mock_conversation_id,
        user_id=mock_user_id,
        title="Test Conversation",
        current_mode="balanced"
    )

    # Add some messages
    conversation.messages = [
        MessageModel(
            id=uuid4(),
            conversation_id=mock_conversation_id,
            role="user",
            content="Hello",
        )
    ]
    return conversation


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_valid_message_returns_200(
    client: AsyncClient,
    mock_user_id,
    mock_conversation_id,
    mock_db_session,
    mock_conversation,
    mocker
):
    """Test that chat endpoint returns 200 on valid message."""
    # Mock dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Mock ConversationService methods
    mocker.patch.object(
        ConversationService,
        'get_conversation',
        return_value=mock_conversation
    )
    mocker.patch.object(
        ConversationService,
        'add_message',
        return_value=None
    )

    # Mock Anthropic client
    mock_stream = mocker.MagicMock()
    mock_stream.__enter__ = mocker.MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = mocker.MagicMock(return_value=None)
    mock_stream.text_stream = iter(["Hello", " world"])

    mocker.patch('anthropic.Anthropic')
    mock_client = mocker.MagicMock()
    mock_client.messages.stream.return_value = mock_stream
    mocker.patch('anthropic.Anthropic', return_value=mock_client)

    request_data = {
        "conversation_id": str(mock_conversation_id),
        "message": "Test message",
        "mode": "balanced",
        "model": "haiku"
    }

    response = await client.post("/api/chat", json=request_data)
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_missing_conversation_id_returns_422(
    client: AsyncClient,
    mock_user_id,
    mock_db_session
):
    """Test that chat endpoint returns 422 when conversation_id is missing."""
    # Mock dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Request without conversation_id
    request_data = {
        "message": "Test message",
        "mode": "balanced",
        "model": "haiku"
    }

    response = await client.post("/api/chat", json=request_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_nonexistent_conversation_returns_404(
    client: AsyncClient,
    mock_user_id,
    mock_conversation_id,
    mock_db_session,
    mocker
):
    """Test that chat endpoint returns 404 for nonexistent conversation."""
    # Mock dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Mock ConversationService.get_conversation to return None
    mocker.patch.object(
        ConversationService,
        'get_conversation',
        return_value=None
    )

    request_data = {
        "conversation_id": str(mock_conversation_id),
        "message": "Test message",
        "mode": "balanced",
        "model": "haiku"
    }

    response = await client.post("/api/chat", json=request_data)
    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_returns_sse_content_type(
    client: AsyncClient,
    mock_user_id,
    mock_conversation_id,
    mock_db_session,
    mock_conversation,
    mocker
):
    """Test that chat endpoint returns SSE content type."""
    # Mock dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Mock ConversationService methods
    mocker.patch.object(
        ConversationService,
        'get_conversation',
        return_value=mock_conversation
    )
    mocker.patch.object(
        ConversationService,
        'add_message',
        return_value=None
    )

    # Mock Anthropic client
    mock_stream = mocker.MagicMock()
    mock_stream.__enter__ = mocker.MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = mocker.MagicMock(return_value=None)
    mock_stream.text_stream = iter(["Hello"])

    mock_client = mocker.MagicMock()
    mock_client.messages.stream.return_value = mock_stream
    mocker.patch('anthropic.Anthropic', return_value=mock_client)

    request_data = {
        "conversation_id": str(mock_conversation_id),
        "message": "Test message",
        "mode": "balanced",
        "model": "haiku"
    }

    response = await client.post("/api/chat", json=request_data)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_uses_correct_model(
    client: AsyncClient,
    mock_user_id,
    mock_conversation_id,
    mock_db_session,
    mock_conversation,
    mocker
):
    """Test that chat endpoint uses the correct Claude model."""
    # Mock dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_user_id
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # Mock ConversationService methods
    mocker.patch.object(
        ConversationService,
        'get_conversation',
        return_value=mock_conversation
    )
    mocker.patch.object(
        ConversationService,
        'add_message',
        return_value=None
    )

    # Mock Anthropic client
    mock_stream = mocker.MagicMock()
    mock_stream.__enter__ = mocker.MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = mocker.MagicMock(return_value=None)
    mock_stream.text_stream = iter(["Response"])

    mock_client = mocker.MagicMock()
    mock_client.messages.stream.return_value = mock_stream
    mocker.patch('anthropic.Anthropic', return_value=mock_client)

    request_data = {
        "conversation_id": str(mock_conversation_id),
        "message": "Test message",
        "mode": "balanced",
        "model": "sonnet"  # Request sonnet model
    }

    response = await client.post("/api/chat", json=request_data)
    assert response.status_code == 200

    # Verify the correct model was used
    mock_client.messages.stream.assert_called_once()
    call_kwargs = mock_client.messages.stream.call_args[1]
    assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
