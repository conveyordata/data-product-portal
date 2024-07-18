from logging import getLogger
from typing import Any

from app.core.aws.boto3_clients import get_client
from app.settings import settings


class RefreshInfrastructureLambda:
    def __init__(self):
        self.enabled = bool(settings.INFRASTRUCTURE_LAMBDA_ARN)
        self.lambda_arn = settings.INFRASTRUCTURE_LAMBDA_ARN
        self.client = get_client("lambda")
        self.logger = getLogger()

    def trigger(self) -> dict[str, Any]:
        if self.enabled:
            response = self.client.invoke(
                FunctionName=self.lambda_arn, InvocationType="Event"
            )
            self.logger.info(response)
            return response
        else:
            self.logger.info("No infrastructure lambda is set up, not triggering.")
            return {"status": "not enabled"}
