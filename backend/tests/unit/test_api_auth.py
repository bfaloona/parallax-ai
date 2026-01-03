"""Unit tests for authentication endpoints.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.dependencies import get_db
from app.models.base import Base


# Test database URL (in-memory SQLite for async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a fresh test database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield async_session

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Create test HTTP client with database override."""

    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_new_user_returns_201(client: AsyncClient):
    """Test that registering a new user returns 201."""
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
async def test_register_duplicate_email_returns_400(client: AsyncClient):
    """Test that registering with duplicate email returns 400."""
    # Register first user
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )

    # Try to register again with same email
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "different456"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_valid_credentials_returns_token(client: AsyncClient):
    """Test that login with valid credentials returns access token."""
    # Register user
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )

    # Login
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
async def test_login_invalid_password_returns_401(client: AsyncClient):
    """Test that login with invalid password returns 401."""
    # Register user
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )

    # Login with wrong password
    response = await client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_401(client: AsyncClient):
    """Test that login with nonexistent user returns 401."""
    response = await client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "testpass123"}
    )
    assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_me_with_valid_token_returns_user(client: AsyncClient):
    """Test that /me endpoint returns user data with valid token."""
    # Register and login
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    login_response = await client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
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
