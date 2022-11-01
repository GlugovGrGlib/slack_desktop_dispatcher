#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import json
from aiohttp import web
from slack.errors import SlackApiError

from api import init_client, send_channel_message, update_msg

logger = logging.getLogger(__name__)


async def index(request) -> web.Response:
    return web.Response(text=str("Let's start"))


async def event_processor(request) -> web.Response:
    payload = await request.json()
    if payload.get('event'):
        try:
            await send_msg(request)
        except SlackApiError as resp:
            logger.error('%s' % resp)
        else:
            msg = 'Successfully sent a message.'
            logger.info(msg)
    return web.Response(text=str(f"{{challenge: {payload.get('challenge')}}}"), content_type='application/json')


async def interact(request) -> web.Response:
    data = await request.text()
    payload = await request.post()
    payload = json.loads(payload['payload'])
    ts = None
    channel = None
    if payload.get('container'):
        ts = payload['container'].get('message_ts')
        channel = payload['container'].get('channel_id')
    try:
        user_id = payload['user'].get('id')
        selected_desk = payload['actions'][0].get('value')
    except KeyError:
        logger.warning("User or desk is missed")
        return web.Response()
    if ts and channel and user_id and selected_desk:
        client = await init_client()
        await update_msg(client, channel=channel, user_id=user_id, ts=ts, selected_desk=selected_desk)
    logger.info(f'Request was recieved \n data: {data} \n payload: {payload}')
    return web.Response(text=str(f"Request was recieved \n data: {data} \n payload: {payload}"))


async def send_msg(request) -> web.Response:
    client = await init_client()
    try:
        await send_channel_message(client, channel='#test')
    except SlackApiError as resp:
        msg = resp
        logger.error('%s' % (resp))
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return web.Response(text=str(msg))
