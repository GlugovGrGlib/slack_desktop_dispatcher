#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from aiohttp import web
from slack.errors import SlackApiError

from api import init_client, send_message


logger = logging.getLogger(__name__)

async def index(request) -> web.Response:
    return web.Response(text=str("Let's start"))

async def send_msg(request) -> web.Response:
    client = init_client()
    try:
        await send_message(client, channel='#random', text='What do you want from me?')
    except SlackApiError as resp:
        msg = resp
        logger.error('%s' % (resp))
    else:
        msg = 'Successfully sent a message.'
        logger.info(msg)
    return web.Response(text=str(msg))
