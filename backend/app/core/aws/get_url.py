import json
from uuid import UUID

import httpx
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment as EnvironmentModel
from app.core.auth.credentials import AWSCredentials
from app.core.aws.boto3_clients import get_client
from app.data_products.model import DataProduct as DataProductModel
from app.settings import settings
from app.users.schema import User


def get_aws_temporary_credentials(role_arn: str, *, actor: User) -> AWSCredentials:
    email = actor.email
    try:
        response = get_client("sts").assume_role(
            RoleArn=role_arn,
            RoleSessionName=email,
        )
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Please contact us on how to integrate with AWS",
        )

    return AWSCredentials(**response.get("Credentials"))


def _get_data_product_role_arn(id: UUID, environment: str, db: Session) -> str:
    environment_context = (
        db.execute(select(EnvironmentModel).where(EnvironmentModel.name == environment))
        .scalar_one()
        .context
    )
    namespace = db.get(DataProductModel, id).namespace
    role_arn = environment_context.replace("{{}}", namespace)
    return role_arn


def get_aws_url(id: UUID, db: Session, actor: User, environment: str) -> str:
    role = _get_data_product_role_arn(id, environment, db)
    json_credentials = get_aws_temporary_credentials(role, actor=actor)

    url_credentials = {
        "sessionId": json_credentials.AccessKeyId,
        "sessionKey": json_credentials.SecretAccessKey,
        "sessionToken": json_credentials.SessionToken,
    }
    json_dump = json.dumps(url_credentials)

    aws_signin_url = "https://signin.aws.amazon.com/federation"
    r = httpx.get(
        aws_signin_url,
        params={
            "Action": "getSigninToken",
            "SessionDuration": 900,
            "Session": json_dump,
        },
    )

    signin_token = json.loads(r.text)

    request = httpx.Request(
        "GET",
        aws_signin_url,
        params={
            "Action": "login",
            "Issuer": settings.HOST,
            "Destination": "https://console.aws.amazon.com/athena/home#/query-editor",
            "SigninToken": signin_token["SigninToken"],
        },
    )

    return str(request.url)
