"""Pytest configuration and shared fixtures for Parallax AI tests."""

import sys
import os
import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory (backend/) to Python path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture
async def client():
    """Create test HTTP client for FastAPI app.

    Usage in tests:
        async def test_endpoint(client):
            response = await client.get("/api/health")
            assert response.status_code == 200
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as test_client:
        yield test_client


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API streaming response.

    Usage in tests:
        def test_chat(mock_anthropic_response, mocker):
            mocker.patch('anthropic.Client.messages.stream', return_value=mock_anthropic_response)
    """
    class MockStream:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        @property
        def text_stream(self):
            return iter(["Hello", " from", " Claude", "!"])

    return MockStream()


@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing."""
    return {
        "message": "What is the meaning of life?",
        "model": "sonnet"
    }


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-123")
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-256-bit-hex")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Clear FastAPI dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()
