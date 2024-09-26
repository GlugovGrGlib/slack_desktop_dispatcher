from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from .config import get_env_variable


app = AsyncApp(token=get_env_variable("SLACK_BOT_TOKEN"))
slack_client = AsyncWebClient(token=get_env_variable("SLACK_BOT_TOKEN"))