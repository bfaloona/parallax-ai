"""Dependency injection functions for Parallax AI.

This module provides FastAPI dependencies that can be injected into route handlers.
Using dependency injection makes the application more testable and maintainable.

Usage:
    from fastapi import Depends
    from app.dependencies import get_anthropic_client

    @app.post("/api/chat")
    async def chat(client: anthropic.Anthropic = Depends(get_anthropic_client)):
        # Use client here
"""

import os
import anthropic
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator, Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.services import ChatService
from app.models.user import User
from app.schemas.auth import TokenData


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://parallax:localdev@postgres:5432/parallax_ai"
)

# Create async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session.

    This dependency creates and yields an async database session.
    The session is automatically closed after the request.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_anthropic_client() -> Generator[anthropic.Anthropic, None, None]:
    """Provide Anthropic client instance.

    This dependency creates and yields an Anthropic client configured with
    the API key from environment variables.

    Yields:
        anthropic.Anthropic: Configured Anthropic client

    Example:
        @app.post("/api/chat")
        async def chat(client: anthropic.Anthropic = Depends(get_anthropic_client)):
            with client.messages.stream(...) as stream:
                # Use stream
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        yield client
    finally:
        # Cleanup if needed (Anthropic client doesn't require explicit cleanup)
        pass


def get_chat_service(
    client: anthropic.Anthropic = Depends(get_anthropic_client)
) -> ChatService:
    """Provide ChatService instance with injected dependencies.

    This dependency creates a ChatService with the Anthropic client
    already injected, following the dependency injection pattern.

    Args:
        client: Anthropic client (injected via Depends)

    Returns:
        ChatService: Configured chat service instance

    Example:
        @app.post("/api/chat")
        async def chat(service: ChatService = Depends(get_chat_service)):
            async for event in service.stream_chat_response("Hello"):
                # Use event
    """
    return ChatService(anthropic_client=client)


# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UUID:
    """Get current user ID from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Current user UUID

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=UUID(user_id))
    except JWTError:
        raise credentials_exception

    # Verify user exists in database
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Return user_id instead of full user object for simplicity
    return user.id


async def get_current_active_user(
    current_user_id: Annotated[UUID, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Get current active user object.

    Args:
        current_user_id: Current user ID from token
        db: Database session

    Returns:
        Active user object

    Raises:
        HTTPException: If user is inactive
    """
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
