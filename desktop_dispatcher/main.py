import asyncio

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from .config import get_env_variable
from .events import *
from .slack_client import app


async def main():
    handler = AsyncSocketModeHandler(app, get_env_variable('SLACK_APP_TOKEN'))
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())