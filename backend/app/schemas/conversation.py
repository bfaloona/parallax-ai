"""Pydantic schemas for conversations and messages."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base schema for messages."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    mode: Optional[str] = Field(None, description="Mode used when message was generated")


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageResponse(MessageBase):
    """Schema for message in API responses."""

    id: UUID
    conversation_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base schema for conversations."""

    title: str = Field(default="New Conversation", max_length=255)
    current_mode: str = Field(default="balanced", description="Current mode for conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(None, max_length=255)
    current_mode: Optional[str] = None


class ModeUpdate(BaseModel):
    """Schema for updating conversation mode."""

    mode: str = Field(..., description="New mode: balanced, challenge, explore, ideate, clarify, plan, audit")


class ConversationResponse(ConversationBase):
    """Schema for conversation in API responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages included."""

    messages: List[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
