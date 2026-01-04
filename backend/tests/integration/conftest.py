"""Integration test fixtures using the existing PostgreSQL container from docker-compose.

This module provides fixtures for integration tests that require a real database.
We use the PostgreSQL container already running via docker-compose instead of testcontainers.

Fixtures:
    test_db_engine: Async SQLAlchemy engine connected to test database
    test_db: Database session with automatic rollback after each test
    test_client: HTTP client with database dependency overridden
    auth_headers: Helper to create JWT authentication headers
"""

import asyncio
import os
from typing import AsyncGenerator, Dict
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.dependencies import get_db, create_access_token
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
def initialize_bcrypt():
    """Initialize bcrypt backend to avoid initialization race conditions in tests.

    This fixture runs automatically at session start and ensures bcrypt is properly
    initialized before any tests run. This prevents bcrypt backend errors in async tests.
    """
    import bcrypt
    # Trigger bcrypt initialization with a dummy hash
    # Use truncated password to avoid 72-byte limit error
    test_password = b"initialization_test"[:72]
    salt = bcrypt.gensalt()
    bcrypt.hashpw(test_password, salt)
    return None


@pytest.fixture(scope="session")
def event_loop():
    """Provide session-scoped event loop for async fixtures.

    This is needed for session-scoped async fixtures like test_db_engine.
    pytest-asyncio provides a function-scoped event_loop by default, but we need
    session scope for database setup/teardown efficiency.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Get database URL for test database.

    Uses the same PostgreSQL instance from docker-compose but creates a separate
    test database to avoid polluting production data.

    Returns:
        Database URL with asyncpg driver for test database
    """
    # Use environment variable or default to docker-compose postgres
    postgres_password = os.getenv("POSTGRES_PASSWORD", "localdev")
    # Connect to parallax_ai_test database (will be created if needed)
    return f"postgresql+asyncpg://parallax:{postgres_password}@postgres:5432/parallax_ai_test"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine(test_db_url):
    """Create async database engine for testing.

    This fixture:
    1. Creates the test database if it doesn't exist
    2. Creates all tables at session start
    3. Drops all tables at session end (but keeps the database)

    Args:
        test_db_url: Database connection URL

    Yields:
        AsyncEngine: SQLAlchemy async engine
    """
    # First, connect to postgres database to create test database
    postgres_password = os.getenv("POSTGRES_PASSWORD", "localdev")
    admin_url = f"postgresql+asyncpg://parallax:{postgres_password}@postgres:5432/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT", echo=False)

    # Create test database if it doesn't exist
    async with admin_engine.connect() as conn:
        # Check if database exists
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='parallax_ai_test'")
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text("CREATE DATABASE parallax_ai_test"))

    await admin_engine.dispose()

    # Now connect to test database and create tables
    engine = create_async_engine(test_db_url, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables (but keep database for next run)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide database session with automatic rollback.

    This fixture creates a new database session for each test and automatically
    rolls back all changes after the test completes. This ensures test isolation.

    Args:
        test_db_engine: Database engine

    Yields:
        AsyncSession: Database session that will be rolled back
    """
    # Create connection with transaction for rollback
    async with test_db_engine.connect() as connection:
        # Begin a transaction
        transaction = await connection.begin()

        # Create session bound to this connection
        async_session = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"  # Allow nested transactions
        )

        async with async_session() as session:
            yield session

        # Rollback the transaction after test completes
        await transaction.rollback()


@pytest_asyncio.fixture
async def test_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database dependency overridden.

    This fixture creates an HTTP client for testing FastAPI endpoints
    with the database dependency overridden to use the test database.

    Args:
        test_db: Test database session

    Yields:
        AsyncClient: HTTP client for testing
    """
    # Override database dependency to use test database
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing.

    This helper fixture returns a function that creates JWT authentication headers
    for a given user ID. Useful for testing authenticated endpoints.

    Returns:
        Function that takes user_id and returns headers dict

    Example:
        async def test_authenticated_endpoint(test_client, auth_headers):
            user_id = UUID("...")
            headers = auth_headers(user_id)
            response = await test_client.get("/api/protected", headers=headers)
    """
    def _create_headers(user_id: UUID) -> Dict[str, str]:
        token = create_access_token(data={"sub": str(user_id)})
        return {"Authorization": f"Bearer {token}"}

    return _create_headers
