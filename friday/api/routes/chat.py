from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from friday.core.brain import FridayBrain

router = APIRouter()
brain = FridayBrain()


class ChatRequest(BaseModel):
    message: str


@router.post("")
async def chat_endpoint(request: ChatRequest):
    """
    Stream the response from FRIDAY's brain via Server-Sent Events (SSE).

    This endpoint takes a JSON payload with a `message` field, passes it to the
    FRIDAY Brain for processing, and streams the chunks back to the client in real-time.

    Args:
        request (ChatRequest): The incoming request payload containing the user message.

    Returns:
        StreamingResponse: An SSE stream of the generated text.
    """

    # Create a generator that yields SSE formatted strings
    def event_generator():
        for chunk in brain.stream_process(request.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
