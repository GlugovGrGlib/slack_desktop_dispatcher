import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)

slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
notification_channel_name = os.getenv("NOTIFICATION_CHANNEL_NAME")


def get_env_variable(variable_name: str) -> str:
    """
    Retrieves the value of the specified environment variable.

    Args:
    - variable_name (str): The name of the environment variable to retrieve.

    Returns:
    - str: The value of the specified environment variable.

    Raises:
    - KeyError: If the specified environment variable is not set.
    """
    try:
        var_value = os.environ[variable_name]
        logging.info(f"Successfully retrieved the {variable_name} environment variable")
        return var_value
    except KeyError:
        error_msg = f"Set the {variable_name} environment variable"
        logging.error(error_msg)
        raise KeyError({"error": error_msg})


def get_channel_id_by_name(channel_name):
    """
    Retrieves the ID of a Slack channel by its name.

    Args:
        channel_name (str): The name of the Slack channel to retrieve the ID for.

    Returns:
        str: The ID of the Slack channel, or None if the channel is not found.
    """
    try:
        response = slack_client.users_conversations()
        channels = response["channels"]
        for channel in channels:
            if channel["name"] == channel_name:
                return channel["id"]
        return None
    except SlackApiError as e:
        logger.error(f"Error fetching channels: {str(e)}")
        return None


def notify_channel(message):
    """
    Sends a message to a specified Slack channel.

    Args:
        message (str): The message to send to the Slack channel.
    """
    channel_id = get_channel_id_by_name(notification_channel_name)
    if not channel_id:
        logger.error(f"Channel {notification_channel_name} not found.")
        return
    try:
        slack_client.chat_postMessage(channel=channel_id, text=message)
    except Exception as e:
        logger.error(f"Failed to send notification to channel: {str(e)}")
