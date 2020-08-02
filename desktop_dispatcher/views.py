#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from aiohttp import web
from slack.errors import SlackApiError

from api import init_client, send_channel_message


logger = logging.getLogger(__name__)

async def index(request) -> web.Response:
    return web.Response(text=str("Let's start"))

async def interact(request) -> web.Response:
    data = await request.text()
    payload = await request.post()
    logger.info(f'Request was recieved \n data: {data} \n payload: {payload}')
    return web.Response(text=str(f"Request was recieved \n data: {data} \n payload: {payload}"))

async def send_msg(request) -> web.Response:
    client = await init_client()
    try:
        await send_channel_message(client, channel='#random')
    except SlackApiError as resp:
        msg = resp
        logger.error('%s' % (resp))
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return web.Response(text=str(msg))
