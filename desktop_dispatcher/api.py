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
import logging
import certifi
import json
import ssl as ssl_lib
from aiohttp_requests import requests
from slack import WebClient
from slack.errors import SlackApiError
from models.models import get_bind, Desktop

from utils import form_select_desktop_block, form_leave_block

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
logger = logging.getLogger()


async def get_available_desktops():
    await get_bind()
    available_desk = await Desktop.query.where(Desktop.occupied == False).gino.all()
    return available_desk


async def get_desktop(desktop: str = None):
    await get_bind()
    desk = await Desktop.query.where(Desktop.name == desktop).gino.first()
    return desk


async def update_occupation(desktop: str = None, occupation: bool = False, uid: str = None):
    await get_bind()
    status = await Desktop.update.values(occupied=occupation, user_id=uid).where(Desktop.name == desktop).gino.status()
    return status


async def construct_button(desk: str = None, style: str = None, text: str = None, need_confirm: bool = False):
    confirm = {
        "title": {
            "type": "plain_text",
            "text": "Are you sure?"
        },
        "confirm": {
            "type": "plain_text",
            "text": text
        },
        "deny": {
            "type": "plain_text",
            "text": "Leave"
        }
    }
    button = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "emoji": True,
            "text": desk
        },
        "style": style,
        "value": desk
    }
    if need_confirm:
        button['confirm'] = confirm
    return button


async def init_client() -> WebClient:
    client = WebClient(
        token=os.getenv('SLACK_BOT_TOKEN'),
        ssl=ssl_context,
        run_async=True
    )
    return client


async def construct_message(desks: list = [], style: str = 'primary', text: str = 'Book', need_confirm: bool = False):
    if not desks:
        return None
    message = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Available desks:*"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [await construct_button(desk.name, style, text, need_confirm) for desk in desks]
        }
    ]
    return message


async def send_channel_message(client: WebClient, channel: str, text='msg'):
    available_desk = await get_available_desktops()
    blocks = await construct_message(available_desk, need_confirm=True)
    try:
        client.chat_postMessage(
            channel=channel,
            text=json.dumps(text),
            blocks=blocks
        )
    except SlackApiError as resp:
        logger.error('%s' % (resp))
        return False
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return True


async def send_dm_message(client: WebClient, channel: str, blocks: str):
    ...


async def send_initial_msg() -> bool:
    client = await init_client()
    channel = "#random"
    blocks = await form_select_desktop_block()
    return await send_channel_message(client, channel, blocks)


async def send_leave_msg() -> bool:
    client = await init_client()
    # user =
    channel = "#random"
    blocks = await form_leave_block()
    return await send_channel_message(client, channel, blocks)


async def delete_msg_by_url(return_url: str):
    resp = requests.post(return_url, data={'delete_original': True})
    return resp


async def update_msg(client: WebClient, channel: str, user_id: str = None, text='UPD', ts: str = None,
                     selected_desk=None):
    desk = await get_desktop(selected_desk)

    try:
        if desk.occupied and desk.user_id == user_id:
            await update_occupation(selected_desk, False)
            client.chat_delete(
                channel=channel,
                ts=ts,
            )
            await send_channel_message(client, '#test', "Someone left the desk")
        else:
            await update_occupation(selected_desk, True, user_id)
            client.chat_delete(
                channel=channel,
                ts=ts,
            )
            client.chat_postMessage(
                channel=user_id,
                text=json.dumps(text),
                blocks=await construct_message([desk], "danger", "Left desk", need_confirm=False)
            )
    except SlackApiError as resp:
        logger.error('%s' % (resp))
        return False
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return True
