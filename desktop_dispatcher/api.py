# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
# slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)
#
#
# # Create an event listener for "reaction_added" events and print the emoji name
# @slack_events_adapter.on("reaction_added")
# def reaction_added(event_data):
#   emoji = event_data["event"]["reaction"]
#   print(emoji)
import os
import certifi
import ssl as ssl_lib
from aiohttp_requests import requests
from slack import WebClient
from slack.errors import SlackApiError

from utils import form_select_desktop_block, form_leave_block


ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

async def init_client() -> WebClient:
    client = WebClient(
        token=os.environ['SLACK_BOT_TOKEN'],
        ssl=ssl_context,
        run_async=True
    )
    return client

async def send_channel_message(client: WebClient, channel: str, text: str = None, blocks: str = None):
    try:
        client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )
    except SlackApiError as resp:
        msg = resp
        logger.error('%s' % (resp))
        return False
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return True

async def send_dm_message(client: WebClient, channel: str, blocks: str):
    ...

async def send_initial_msg() ->  bool:
    client = await init_client()
    channel = "#random"
    blocks = await form_select_desktop_block()
    return await send_channel_message(client, channel,  blocks)


async def send_leave_msg() -> bool:
    client = await init_client()
    # user =
    channel = "#random"
    blocks = await form_leave_block()
    return await send_channel_message(client, channel,  blocks)

async def delete_msg_by_url(return_url: str):
    resp = requests.post(return_url, data = {'delete_original': True})
    return resp
