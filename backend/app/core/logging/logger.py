from logging import getLogger, INFO, config, Logger
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logger(prefix: str = "local") -> Logger:
    config.fileConfig(
        os.path.join("app", "core", "logging", "logging.conf"),
        disable_existing_loggers=False,
    )
    logger = getLogger("root")

    logging_dir = os.getenv("LOGGING_DIRECTORY", "/var/logs")

    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

    fh = TimedRotatingFileHandler(
        os.path.join(logging_dir, prefix), when="MIDNIGHT", interval=1
    )
    fh.suffix = "%Y%m%d.log"
    fh.setLevel(INFO)
    logger.addHandler(fh)
    return logger
