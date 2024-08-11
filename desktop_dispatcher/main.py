from slack_bolt.adapter.socket_mode import SocketModeHandler

from .events import app
from .utils import get_env_variable


if __name__ == "__main__":
    SocketModeHandler(app, get_env_variable('SLACK_APP_TOKEN')).start()
