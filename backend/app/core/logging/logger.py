import json
import logging
import logging.config
import os

from app.settings import LoggerConfig

settings = LoggerConfig()

LOG_LEVEL = getattr(logging, settings.LOG_LEVEL)
LOG_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), settings.LOG_CONFIG_FILE
)


def get_logger(name: str, prefix: str = "local"):
    dict_config = json.load(open(LOG_CONFIG_PATH))
    dict_config["handlers"]["fileHandler"]["filename"] = os.path.join(
        settings.LOGGING_DIRECTORY, prefix
    )

    if not os.path.exists(settings.LOGGING_DIRECTORY):
        os.makedirs(settings.LOGGING_DIRECTORY)

    logging.config.dictConfig(dict_config)

    app_logger = logging.getLogger(name)
    app_logger.setLevel(LOG_LEVEL)
    return app_logger


logger = get_logger(__name__)
