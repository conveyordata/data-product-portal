from botocore.client import BaseClient
from botocore.exceptions import NoRegionError
from fastapi import HTTPException, status

from app.core.aws.refreshable_session import RefreshableBotoSession
from app.core.logging.logger import logger

disabled_aws = False
try:
    session = RefreshableBotoSession().refreshable_session()
    clients = {
        "s3": session.client("s3"),
        "sts": session.client("sts"),
        "lambda": session.client("lambda"),
    }
except (AttributeError, NoRegionError):
    logger.warning(
        "Could not instantiate AWS session. All AWS functionality will be disabled"
    )
    disabled_aws = True


def get_client(client_name: str) -> BaseClient:
    if disabled_aws:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AWS is not initialized, this request can not be executed",
        )

    if not clients.get(client_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "AWS client is not initialized, "
                "please update your code to be able to execute this request",
            ),
        )
    return clients.get(client_name)
