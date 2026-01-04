"""Chat streaming endpoint using Claude API."""

import os
import json
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import anthropic

from app.dependencies import get_db, get_current_user
from app.services.conversation_service import ConversationService
from app.schemas.conversation import MessageCreate

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    conversation_id: str
    message: str
    mode: str = "balanced"
    model: str = "haiku"


# Model mapping
MODEL_MAP = {
    "haiku": "claude-3-5-haiku-20241022",
    "sonnet": "claude-3-5-sonnet-20241022",
    "opus": "claude-opus-4-20250514",
}

# Simple mode prompts (balanced only for now)
MODE_PROMPTS = {
    "balanced": "You are a helpful AI assistant. Provide clear, accurate, and balanced responses."
}


@router.post("", response_class=StreamingResponse)
async def chat_stream(
    request: ChatRequest,
    current_user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stream chat responses from Claude API.

    Saves user message and assistant response to database.
    Returns SSE stream of assistant response.
    """
    # Verify conversation belongs to user
    conversation = await ConversationService.get_conversation(
        db, UUID(request.conversation_id), current_user_id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message to database
    user_message_data = MessageCreate(
        role="user",
        content=request.message,
        mode=request.mode
    )
    await ConversationService.add_message(
        db, UUID(request.conversation_id), current_user_id, user_message_data
    )

    # Get conversation history for context
    convo_with_messages = await ConversationService.get_conversation(
        db, UUID(request.conversation_id), current_user_id
    )

    # Build messages array for Claude API
    messages = []
    for msg in convo_with_messages.messages:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Get system prompt
    system_prompt = MODE_PROMPTS.get(request.mode, MODE_PROMPTS["balanced"])

    # Get Claude model
    model_id = MODEL_MAP.get(request.model, MODEL_MAP["haiku"])

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream from Claude API."""
        assistant_response = ""

        try:
            with client.messages.stream(
                model=model_id,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    assistant_response += text
                    # Send SSE event
                    yield f"data: {json.dumps({'content': text})}\n\n"

            # Stream completed successfully
            yield f"data: {json.dumps({'done': True})}\n\n"

            # Save assistant response to database
            assistant_message_data = MessageCreate(
                role="assistant",
                content=assistant_response,
                mode=request.mode
            )
            await ConversationService.add_message(
                db, UUID(request.conversation_id), current_user_id, assistant_message_data
            )

        except Exception as e:
            error_message = str(e)
            yield f"data: {json.dumps({'error': error_message})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
