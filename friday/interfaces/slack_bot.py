import logging
import os
import sys
import time
import traceback

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from friday.core.brain import FridayBrain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make sure we can import from friday
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

load_dotenv()

print("[FRIDAY Slack] Initializing app...")
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
print("[FRIDAY Slack] Initializing brain...")
try:
    brain = FridayBrain()
    print("[FRIDAY Slack] Brain initialized successfully.")
except Exception as e:
    print(f"[FRIDAY Slack] FAILED to initialize brain: {e}")
    traceback.print_exc()
    sys.exit(1)


def process_and_stream_reply(event, say, client):
    """
    Handles streaming the LLM response back to Slack while updating the message
    in real-time to create a typing effect without hitting rate limits.
    """
    channel = event.get("channel")
    ts = event.get("ts")
    thread_ts = event.get("thread_ts", ts)
    user_text = event.get("text", "")

    logger.info(f"Processing message from channel {channel}: {user_text[:50]}...")

    # Strip the bot mention if it exists
    if "<@" in user_text:
        user_text = user_text.split(">", 1)[-1].strip()

    # 1. Acknowledge with an 'eyes' emoji
    try:
        client.reactions_add(channel=channel, name="eyes", timestamp=ts)
    except SlackApiError as e:
        logger.warning(f"Failed to add eyes reaction: {e}")

    # 2. Post the initial placeholder message
    try:
        initial_msg = say(text="*Processing...* 🧠", thread_ts=thread_ts)
        reply_ts = initial_msg["ts"]
    except Exception as e:
        print(f"Failed to send initial message: {e}")
        return

    # 3. Stream chunks from the brain
    full_text = ""
    last_update_time = time.time()

    for chunk in brain.stream_process(user_text):
        full_text += chunk
        logger.debug(f"Received chunk: {chunk}")

        # Slack Rate Limit: 1 update per second. We use 1.5s to be safe.
        if time.time() - last_update_time > 1.5:
            try:
                logger.info(f"Updating Slack message with {len(full_text)} chars...")
                client.chat_update(channel=channel, ts=reply_ts, text=full_text + " ⏳")
                last_update_time = time.time()
            except SlackApiError as e:
                logger.error(f"Rate limit hit or update error: {e}")

    # 4. Final update with the complete text
    try:
        logger.info("Finalizing Slack message.")
        client.chat_update(channel=channel, ts=reply_ts, text=full_text)
        client.reactions_remove(channel=channel, name="eyes", timestamp=ts)
        client.reactions_add(channel=channel, name="white_check_mark", timestamp=ts)
    except SlackApiError as e:
        logger.error(f"Final update failed: {e}")


@app.event("app_mention")
def handle_app_mention(event, say, client):
    """Triggered when @Friday-Agent is mentioned in a channel."""
    process_and_stream_reply(event, say, client)


@app.event("message")
def handle_message(event, say, client):
    """Triggered on direct messages to the bot."""
    # Ignore messages from bots to prevent loops
    if event.get("bot_id"):
        return

    channel_type = event.get("channel_type")

    # Respond immediately if it's a DM
    if channel_type == "im":
        process_and_stream_reply(event, say, client)


def _get_handler():
    """Build and return a SocketModeHandler, or None if tokens are missing."""
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token or not app_token.startswith("xapp-"):
        logger.error(
            "[FRIDAY Slack] SLACK_APP_TOKEN is missing or invalid -- Slack bot disabled."
        )
        return None
    try:
        return SocketModeHandler(app, app_token)
    except Exception as e:
        logger.error(f"[FRIDAY Slack] Failed to initialize SocketModeHandler: {e}")
        return None


def send_startup_notification():
    """Send a 'System Online' message to the configured channel."""
    channel_id = os.environ.get("SLACK_CHANNEL_ID")
    if not channel_id:
        return

    try:
        app.client.chat_postMessage(
            channel=channel_id,
            text="*FRIDAY System Online* ⚡\nAll systems nominal, Boss. I'm connected and listening.",
        )
        logger.info(f"Sent startup notification to {channel_id}")
    except SlackApiError as e:
        logger.warning(f"Could not send startup notification: {e.response['error']}")
    except Exception as e:
        logger.error(f"Error sending startup notification: {e}")


def start_in_background() -> None:
    """
    Start the Slack Socket Mode bot in a daemon thread with a retry loop.
    """
    import threading

    def _run():
        backoff = 5
        while True:
            handler = _get_handler()
            if handler is None:
                logger.warning("[FRIDAY Slack] No valid handler, retrying in 30s...")
                time.sleep(30)
                continue

            try:
                logger.info("[FRIDAY Slack] Connecting to Slack Socket Mode...")
                handler.connect()
                logger.info("[FRIDAY Slack] Connected. Bot is live and listening.")

                # Send a quick notification that we're back online
                send_startup_notification()

                # Block the daemon thread so the connection stays open
                # We use a loop to check if the client is still connected
                while handler.client.is_connected():
                    time.sleep(5)

                logger.warning(
                    "[FRIDAY Slack] Connection lost. Attempting to reconnect..."
                )
            except Exception as e:
                logger.error(f"[FRIDAY Slack] Connection error: {e}")

            logger.info(f"[FRIDAY Slack] Retrying in {backoff} seconds...")
            time.sleep(backoff)
            backoff = min(backoff * 2, 300)  # Exponential backoff up to 5 minutes

    t = threading.Thread(target=_run, name="friday-slack-bot", daemon=True)
    t.start()


def start_bot() -> None:
    """Blocking entry point -- used when running as __main__."""
    handler = _get_handler()
    if handler is None:
        return
    print("[FRIDAY Slack] Starting in Socket Mode (foreground)...")
    send_startup_notification()
    handler.start()


if __name__ == "__main__":
    start_bot()
