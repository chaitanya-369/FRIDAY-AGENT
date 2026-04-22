from fastapi import APIRouter, Request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from friday.config.settings import settings
import logging

router = APIRouter(prefix="/slack", tags=["slack"])
logger = logging.getLogger(__name__)

# Note: Ensure you have SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET in your settings
slack_client = WebClient(token=getattr(settings, "slack_bot_token", ""))


@router.post("/events")
async def slack_events(request: Request):
    payload = await request.json()

    # Slack URL verification challenge
    if "challenge" in payload:
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})
    event_type = event.get("type")

    if event_type == "message" and "bot_id" not in event:
        # Handle incoming message event
        channel_id = event.get("channel")
        text = event.get("text")
        try:
            # Echo back or process the message
            slack_client.chat_postMessage(
                channel=channel_id, text=f"FRIDAY received: {text}"
            )
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")

    return {"status": "ok"}
