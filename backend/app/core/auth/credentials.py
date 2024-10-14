from datetime import datetime

from pydantic import BaseModel


class AWSCredentials(BaseModel):
    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: datetime
