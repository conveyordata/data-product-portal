from pydantic import BaseModel
from datetime import datetime


class AWSCredentials(BaseModel):
    AccessKeyId: str
    SecretAccessKey: str
    SessionToken: str
    Expiration: datetime
