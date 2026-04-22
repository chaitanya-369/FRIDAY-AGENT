import sys
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables from the project root .env
load_dotenv()


def send_notification(message: str):
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL_ID", "#general")

    if not token or "your_slack_bot_token" in token:
        print(
            "\n[!] SLACK_BOT_TOKEN is missing or placeholder. Skipping Slack notification."
        )
        print(f"[?] Message would have been: {message}")
        print("[i] Set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID in .env to enable.\n")
        return

    client = WebClient(token=token)
    try:
        client.chat_postMessage(
            channel=channel, text=f"🤖 *Antigravity Update:*\n{message}"
        )
        print(f"[+] Notification sent to {channel} successfully.")
    except SlackApiError as e:
        print(f"[-] Error sending to Slack: {e.response['error']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        send_notification(msg)
    else:
        print("Usage: python notify.py 'Your message here'")
