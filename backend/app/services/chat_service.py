"""Chat service for handling Claude API interactions.

This service encapsulates the business logic for chat functionality,
separating it from the HTTP layer (routes) for better testability
and maintainability.
"""

from typing import AsyncGenerator, Dict
import anthropic


class ChatService:
    """Service for handling chat interactions with Claude API.

    This service manages streaming responses from the Claude API,
    handling the complexity of streaming SSE responses.

    Attributes:
        client: Anthropic client instance for API calls
        default_model: Default Claude model to use
        default_max_tokens: Default maximum tokens for responses
    """

    def __init__(
        self,
        anthropic_client: anthropic.Anthropic,
        default_model: str = "claude-sonnet-4-20250514",
        default_max_tokens: int = 4096
    ):
        """Initialize ChatService.

        Args:
            anthropic_client: Configured Anthropic client
            default_model: Model ID to use (default: claude-sonnet-4-20250514)
            default_max_tokens: Maximum tokens in response (default: 4096)
        """
        self.client = anthropic_client
        self.default_model = default_model
        self.default_max_tokens = default_max_tokens

    async def stream_chat_response(
        self,
        message: str,
        model: str | None = None,
        max_tokens: int | None = None
    ) -> AsyncGenerator[Dict[str, str], None]:
        """Stream a chat response from Claude API.

        This method handles the streaming response from Claude, yielding
        Server-Sent Events (SSE) formatted messages.

        Args:
            message: User message to send to Claude
            model: Model to use (defaults to self.default_model)
            max_tokens: Max tokens (defaults to self.default_max_tokens)

        Yields:
            Dict with 'event' and 'data' keys for SSE format

        Example:
            async for event in service.stream_chat_response("Hello"):
                # event = {"event": "message", "data": "Hello..."}
        """
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens

        with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": message}]
        ) as stream:
            for text in stream.text_stream:
                yield {"event": "message", "data": text}

        # Signal end of stream
        yield {"event": "done", "data": ""}
