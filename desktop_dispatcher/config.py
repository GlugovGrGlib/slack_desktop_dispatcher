import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


def get_env_variable(variable_name: str) -> str:
    try:
        var_value = os.environ[variable_name]
        logging.info(f"Successfully retrieved the {variable_name} environment variable")
        return var_value
    except KeyError:
        error_msg = f"Set the {variable_name} environment variable"
        logging.error(error_msg)
        raise KeyError({"error": error_msg})

notification_channel_name = os.getenv("NOTIFICATION_CHANNEL_NAME")