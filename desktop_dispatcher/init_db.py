import asyncio
import gino

from settings import get_config
from models.models import get_bind, Desktop

config = get_config()
db = gino.Gino()


async def init_db():
    await get_bind()
    desktops = config['available_desktop'].split(',')
    for desktop in desktops:
        try:
            desktop = Desktop(user_id=None, name=desktop, occupied=False)
            await desktop.create()
        except:
            pass


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(init_db())
