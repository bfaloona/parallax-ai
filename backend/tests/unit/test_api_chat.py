"""Unit tests for chat endpoint.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

Example:
    test_chat_endpoint_valid_message_returns_200()
"""

import pytest
from httpx import AsyncClient
from typing import AsyncGenerator, Dict

from app.main import app
from app.dependencies import get_chat_service
from app.services import ChatService


class MockChatService(ChatService):
    """Mock ChatService for testing."""

    def __init__(self, response_chunks=None):
        # Don't call super().__init__() - we don't need real client
        self.response_chunks = response_chunks or ["Hello", " world"]
        self.last_message = None
        self.last_model = None
        self.last_max_tokens = None

    async def stream_chat_response(
        self,
        message: str,
        model: str | None = None,
        max_tokens: int | None = None
    ) -> AsyncGenerator[Dict[str, str], None]:
        """Mock streaming response."""
        # Store params for verification
        self.last_message = message
        self.last_model = model
        self.last_max_tokens = max_tokens

        # Yield mock chunks
        for chunk in self.response_chunks:
            yield {"event": "message", "data": chunk}
        yield {"event": "done", "data": ""}


@pytest.fixture
def mock_chat_service():
    """Factory fixture for creating mock chat service."""
    def _create_mock(response_chunks=None):
        return MockChatService(response_chunks)
    return _create_mock


@pytest.mark.unit
@pytest.mark.asyncio
async def test_chat_endpoint_valid_message_returns_200(
    client: AsyncClient,
    sample_chat_message,
    mock_chat_service
):
    """Test that chat endpoint returns 200 on valid message."""
    mock_service = mock_chat_service()
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = await client.post("/api/chat", json=sample_chat_message)
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="SSE event loop conflicts - will fix in Phase 2")
async def test_chat_endpoint_empty_message_returns_200(
    client: AsyncClient,
    mock_chat_service
):
    """Test that chat endpoint handles empty message gracefully."""
    mock_service = mock_chat_service([])
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = await client.post("/api/chat", json={"message": ""})
    assert response.status_code == 200
    assert mock_service.last_message == ""


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="SSE event loop conflicts - will fix in Phase 2")
async def test_chat_endpoint_valid_message_passes_message_to_service(
    client: AsyncClient,
    sample_chat_message,
    mock_chat_service
):
    """Test that chat endpoint passes user message to chat service."""
    mock_service = mock_chat_service()
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    await client.post("/api/chat", json=sample_chat_message)
    assert mock_service.last_message == sample_chat_message["message"]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="SSE event loop conflicts - will fix in Phase 2")
async def test_chat_endpoint_missing_message_field_uses_empty_string(
    client: AsyncClient,
    mock_chat_service
):
    """Test that chat endpoint handles missing message field with empty string."""
    mock_service = mock_chat_service([])
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = await client.post("/api/chat", json={})
    assert response.status_code == 200
    assert mock_service.last_message == ""


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="SSE event loop conflicts - will fix in Phase 2")
async def test_chat_endpoint_streams_response_events(
    client: AsyncClient,
    sample_chat_message,
    mock_chat_service
):
    """Test that chat endpoint streams SSE events correctly."""
    mock_service = mock_chat_service(["Hello", " world"])
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    response = await client.post("/api/chat", json=sample_chat_message)
    assert response.status_code == 200

    # Verify we got SSE content type
    assert "text/event-stream" in response.headers.get("content-type", "")
