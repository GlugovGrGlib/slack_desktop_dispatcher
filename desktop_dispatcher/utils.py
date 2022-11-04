#!/usr/bin/env python
# -*- coding: utf-8 -*-

import trafaret as T


TRAFARET = T.Dict({
    T.Key('database'):
        T.Dict({
            'db_driver': T.String(),
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
            'retry_limit': T.Int(),
            'retry_interval': T.Int(),
            'ssl': T.ToBool(),
            'echo': T.ToBool(),
        }),
    T.Key('host'): T.String(),
    T.Key('port'): T.Int(),
    T.Key('available_desktop'): T.String(),
    T.Key('channel_name'): T.String()
})

async def form_text_block(string: str) -> dict:
    block = dict(
        type="section",
        text=dict(
            type="mrkdwn",
            text=string
        )
    )
    return block

async def form_actions_block(buttons: list) -> dict:
    elements = [dict(
        type="button",
        text=dict(
            type="plain_text",
            text=button[0],
            emoji=True
        ),
        value=button[1]
    ) for button in buttons]

    block = dict(
        type="actions",
        elements=elements
    )
    return block

async def form_select_desktop_block() -> list:
    """Generate interacive block to send to common channel."""
    blocks = list()
    append = blocks.append

    # Query db if any of desktops is available
    available_opt = []
    msg = "Please select desktop" if available_opt else "No desktops are available at the time"
    append(form_text_block(msg))
    append(form_actions_block([["Desktop 1 (Max)", "desktop1"], ["Desktop 2 (Olga)", "desktop2"]]))
    return blocks

async def form_leave_block(desktop: str):
    """Generate interactive block to send to dm."""
    blocks = list()
    append = blocks.append

    append(form_text_block(f"Are  you ready to leave {desktop}?"))
    append(form_actions_block([["Leave Now!", "leave"]]))
    return blocks
