import json
from urllib import parse
from uuid import UUID

import httpx
from botocore.exceptions import ClientError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.auth.credentials import AWSCredentials
from app.core.aws.boto3_clients import get_client
from app.data_products.service import DataProductService
from app.integration_providers.integration_provider import IntegrationProvider
from app.users.schema import User


class AWSIntegrationProvider(IntegrationProvider):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_aws_temporary_credentials(
        self, role_arn: str, *, actor: User
    ) -> AWSCredentials:
        try:
            response = get_client("sts").assume_role(
                RoleArn=role_arn,
                RoleSessionName=actor.email,
            )
            return AWSCredentials(**response["Credentials"])
        except ClientError:
            raise HTTPException(
                status_code=501,
                detail="Please contact us on how to integrate with AWS",
            )

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        role = DataProductService(self.db).get_data_product_role_arn(id, environment)
        creds = self.get_aws_temporary_credentials(role, actor=actor)

        session = {
            "sessionId": creds.AccessKeyId,
            "sessionKey": creds.SecretAccessKey,
            "sessionToken": creds.SessionToken,
        }
        signin_token_url = (
            f"https://signin.aws.amazon.com/federation"
            f"?Action=getSigninToken"
            f"&SessionDuration=900"
            f"&Session={parse.quote_plus(json.dumps(session))}"
        )
        token = httpx.get(signin_token_url).json()["SigninToken"]
        return (
            "https://signin.aws.amazon.com/federation"
            f"?Action=login"
            f"&Issuer=portal.demo1.conveyordata.com"
            f"&Destination={parse.quote_plus(
                'https://console.aws.amazon.com/athena/home#/query-editor'
            )}"
            f"&SigninToken={token}"
        )
