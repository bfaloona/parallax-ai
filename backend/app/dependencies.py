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
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends

from app.services import ChatService


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
