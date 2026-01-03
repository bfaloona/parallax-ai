"""Conversation CRUD endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ModeUpdate,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conversations for the current user.

    Returns conversations ordered by most recently updated first.
    """
    conversations = await ConversationService.get_user_conversations(db, current_user_id)
    return conversations


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation.

    The conversation will be owned by the current user.
    """
    conversation = await ConversationService.create_conversation(
        db, current_user_id, conversation_data
    )
    return conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a conversation with all its messages.

    Returns 404 if conversation not found or doesn't belong to current user.
    """
    conversation = await ConversationService.get_conversation(
        db, conversation_id, current_user_id
    )
    return conversation


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    update_data: ConversationUpdate,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a conversation's title or mode.

    Returns 404 if conversation not found or doesn't belong to current user.
    """
    conversation = await ConversationService.update_conversation(
        db, conversation_id, current_user_id, update_data
    )
    return conversation


@router.patch("/{conversation_id}/mode", response_model=ConversationResponse)
async def update_conversation_mode(
    conversation_id: UUID,
    mode_data: ModeUpdate,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a conversation's mode.

    Returns 404 if conversation not found or doesn't belong to current user.
    """
    conversation = await ConversationService.update_conversation_mode(
        db, conversation_id, current_user_id, mode_data.mode
    )
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    Returns 404 if conversation not found or doesn't belong to current user.
    Returns 204 No Content on successful deletion.
    """
    await ConversationService.delete_conversation(db, conversation_id, current_user_id)
    return None


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a message to a conversation.

    Returns 404 if conversation not found or doesn't belong to current user.
    """
    message = await ConversationService.add_message(
        db, conversation_id, current_user_id, message_data
    )
    return message
