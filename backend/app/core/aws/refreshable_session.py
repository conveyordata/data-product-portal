from datetime import datetime, timedelta, timezone
from typing import TypedDict

from boto3 import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session


class RefreshableSessionMetadata(TypedDict):
    access_key: str
    secret_key: str
    token: str | None
    expiry_time: str


def get_refreshable_session(
    region_name=None,
    profile_name=None,
    sts_arn=None,
    session_name="default-session",
    session_ttl=3000,
):
    def refresh_credentials() -> RefreshableSessionMetadata:
        base_session = Session(region_name=region_name, profile_name=profile_name)

        if sts_arn:
            response = base_session.client("sts", region_name=region_name).assume_role(
                RoleArn=sts_arn,
                RoleSessionName=session_name,
                DurationSeconds=session_ttl,
            )["Credentials"]
            return {
                "access_key": response["AccessKeyId"],
                "secret_key": response["SecretAccessKey"],
                "token": response["SessionToken"],
                "expiry_time": response["Expiration"].isoformat(),
            }

        credentials = base_session.get_credentials()
        if credentials is None:
            raise RuntimeError(
                "No AWS credentials available for the configured session."
            )

        frozen = credentials.get_frozen_credentials()
        return {
            "access_key": frozen.access_key,
            "secret_key": frozen.secret_key,
            "token": frozen.token,
            "expiry_time": (
                datetime.now(timezone.utc) + timedelta(seconds=session_ttl)
            ).isoformat(),
        }

    refreshable_credentials = RefreshableCredentials.create_from_metadata(
        metadata=refresh_credentials(),
        refresh_using=refresh_credentials,
        method="sts-assume-role" if sts_arn else "session-credentials",
    )

    session = get_session()
    session._credentials = refreshable_credentials
    session.set_config_variable("region", region_name)

    return Session(botocore_session=session)
