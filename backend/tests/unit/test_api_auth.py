"""Unit tests for authentication endpoints.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

NOTE: These tests mock the database layer to avoid SQLite/UUID incompatibility.
They verify the API contract and business logic without requiring PostgreSQL.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.main import app
from app.dependencies import get_db
from app.models.user import User


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return AsyncMock()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_new_user_returns_201(client: AsyncClient, mock_db):
    """Test that registering a new user returns 201."""
    from datetime import datetime

    # Mock query result for existing user check (no existing user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Mock the refresh to set all required fields on the user
    async def mock_refresh(user):
        user.id = uuid4()
        user.tier = "free"
        user.is_active = True
        user.created_at = datetime.utcnow()

    mock_db.refresh = mock_refresh

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["tier"] == "free"
    assert "id" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_duplicate_email_returns_400(client: AsyncClient, mock_db):
    """Test that registering with duplicate email returns 400."""
    # Mock query result for existing user check (user exists)
    existing_user = User(id=uuid4(), email="test@example.com", tier="free")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db.execute.return_value = mock_result

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "different456"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_valid_credentials_returns_token(client: AsyncClient, mock_db):
    """Test that login with valid credentials returns access token."""
    # Create mock user with valid password
    mock_user = User(id=uuid4(), email="test@example.com", tier="free")
    mock_user.set_password("testpass123")
    mock_user.is_active = True

    # Mock query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_invalid_password_returns_401(client: AsyncClient, mock_db):
    """Test that login with invalid password returns 401."""
    # Create mock user with different password
    mock_user = User(id=uuid4(), email="test@example.com", tier="free")
    mock_user.set_password("correctpassword")
    mock_user.is_active = True

    # Mock query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_result

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_401(client: AsyncClient, mock_db):
    """Test that login with nonexistent user returns 401."""
    # Mock query result (no user found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = await client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "testpass123"}
    )
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_me_with_valid_token_returns_user(client: AsyncClient, mock_db):
    """Test that /me endpoint returns user data with valid token."""
    from app.dependencies import get_current_active_user
    from datetime import datetime

    # Mock user with all required fields
    mock_user = User(
        id=uuid4(),
        email="test@example.com",
        tier="free",
        is_active=True,
        created_at=datetime.utcnow()
    )

    # Override get_current_active_user dependency
    app.dependency_overrides[get_current_active_user] = lambda: mock_user

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["tier"] == "free"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_me_without_token_returns_401(client: AsyncClient):
    """Test that /me endpoint returns 401 without token."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_me_with_invalid_token_returns_401(client: AsyncClient):
    """Test that /me endpoint returns 401 with invalid token."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401
