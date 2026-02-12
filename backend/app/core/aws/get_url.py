import json
from urllib import parse
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

    request_parameters = "?Action=getSigninToken"
    SESSION_DURATION = 900
    request_parameters += f"&SessionDuration={SESSION_DURATION}"
    request_parameters += f"&Session={parse.quote_plus(json_dump)}"
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    r = httpx.get(request_url)

    signin_token = json.loads(r.text)

    request_parameters = "?Action=login"
    request_parameters += f"&Issuer={settings.HOST}"
    athena_link = "https://console.aws.amazon.com/athena/home#/query-editor"
    request_parameters += f"&Destination={parse.quote_plus(athena_link)}"
    request_parameters += f"&SigninToken={signin_token['SigninToken']}"
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    return request_url
