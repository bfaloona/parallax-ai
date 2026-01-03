"""Service layer for conversation and message operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate


class ConversationService:
    """Service for managing conversations and messages."""

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: UUID,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=conversation_data.title,
            current_mode=conversation_data.current_mode
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_user_conversations(
        db: AsyncSession,
        user_id: UUID
    ) -> List[Conversation]:
        """Get all conversations for a user, ordered by most recent first."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID
    ) -> Conversation:
        """
        Get a conversation with messages.

        Raises HTTPException if conversation not found or doesn't belong to user.
        """
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return conversation

    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
        update_data: ConversationUpdate
    ) -> Conversation:
        """
        Update a conversation.

        Raises HTTPException if conversation not found or doesn't belong to user.
        """
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)

        # Update fields if provided
        if update_data.title is not None:
            conversation.title = update_data.title
        if update_data.current_mode is not None:
            conversation.current_mode = update_data.current_mode

        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def update_conversation_mode(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
        mode: str
    ) -> Conversation:
        """
        Update conversation mode.

        Raises HTTPException if conversation not found or doesn't belong to user.
        """
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        conversation.current_mode = mode
        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete a conversation and all its messages.

        Raises HTTPException if conversation not found or doesn't belong to user.
        """
        # Verify ownership first
        await ConversationService.get_conversation(db, conversation_id, user_id)

        # Delete conversation (messages cascade automatically)
        await db.execute(
            delete(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        await db.commit()

    @staticmethod
    async def add_message(
        db: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
        message_data: MessageCreate
    ) -> Message:
        """
        Add a message to a conversation.

        Raises HTTPException if conversation not found or doesn't belong to user.
        """
        # Verify conversation exists and belongs to user
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)

        message = Message(
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            mode=message_data.mode
        )
        db.add(message)

        # Update conversation's updated_at
        conversation.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(message)
        return message
