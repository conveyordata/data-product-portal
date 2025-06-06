from typing import Any

from botocore.exceptions import ClientError

from app.core.aws.boto3_clients import get_client
from app.core.logging import logger
from app.settings import settings


class RefreshInfrastructureLambda:
    def __init__(self):
        self.lambda_arn = settings.INFRASTRUCTURE_LAMBDA_ARN
        self.logger = logger
        if self.lambda_arn:
            self.client = get_client("lambda")

    def trigger(self) -> dict[str, Any]:
        if self.lambda_arn:
            try:
                response = self.client.invoke(
                    FunctionName=self.lambda_arn, InvocationType="Event"
                )
                self.logger.info(response)
                return response
            except ClientError:
                self.logger.warning("Triggering failed", exc_info=1)
                return {"status": "triggering failed"}
        else:
            self.logger.info("No infrastructure lambda is set up, not triggering.")
            return {"status": "not enabled"}
