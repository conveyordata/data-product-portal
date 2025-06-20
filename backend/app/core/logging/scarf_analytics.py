import platform

import requests

from app.core.logging.logger import logger
from app.settings import LoggerConfig


def backend_analytics(api_version: str):
    settings = LoggerConfig()

    try:
        # If either environment variable is set, do not collect metrics and exit.
        if not settings.SCARF_NO_ANALYTICS and not settings.DO_NOT_TRACK:
            requests.get(
                "https://dataminded.gateway.scarf.sh/telemetry",
                params={
                    "version": api_version,
                    "platform": platform.system(),
                    "python": platform.python_version(),
                    "arch": platform.machine(),
                    "sandbox": str(settings.SANDBOX),
                },
            )
    except Exception as e:
        logger.warning(f"Unable to connect to scarf: {e}")
