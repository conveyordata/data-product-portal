import json
from typing import Dict
from uuid import UUID

from pydantic import RootModel, field_validator

from app.shared.schema import IdNameSchema, ORMModel


class Environment(ORMModel):
    name: str
    context: str | None = None
    is_default: bool = False


class GetEnvironment(Environment):
    id: UUID


class _AWSS3Config(ORMModel):
    identifier: str
    bucket_name: str
    arn: str
    kms_key: str


class _AWSGlueConfig(ORMModel):
    identifier: str
    database: str
    account_id: str
    arn: str
    kms_key: str


class Config(RootModel[Dict[str, _AWSS3Config]]):
    pass


class EnvPlatformServiceConfig(ORMModel):
    id: UUID
    config: Config

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class EnvPlatformServiceConfigGet(EnvPlatformServiceConfig):
    platform: IdNameSchema
    service: IdNameSchema
    environment: IdNameSchema


class CreateConfigSchema(ORMModel):
    platform_id: UUID
    service_id: UUID
    config: Config


class ServiceConfig(IdNameSchema):
    identifiers: list[str]


class PlatformConfig(IdNameSchema):
    services: list[ServiceConfig]


class PlatformServiceSetting(ORMModel):
    platform_name: str
    platform_id: UUID
    service_name: str
    service_id: UUID
    configs: list[_AWSS3Config | _AWSGlueConfig]


class EnvironmentSetting(ORMModel):
    name: str
    is_default: bool = False
    settings: list[PlatformServiceSetting]


class EnvironmentsConfigurations(ORMModel):
    platforms: list[PlatformConfig]
    environments: list[EnvironmentSetting]


# a = {
#   "platforms": [
#     {
#       "name": "AWS",
#       "id": "8e99f3e5-5c12-4800-9c21-42cb429f20b3",
#       "services": [
#         {
#           "name": "S3",
#           "id": "f503376c-fc49-40e3-8a3d-ee80804e0fe4",
#           "identifiers": [
#             "s3"
#           ]
#         },
#         {
#           "name": "Glue",
#           "id": "c62a7401-23d9-4dd6-9885-f5b8f5cf760b",
#           "identifiers": [
#             "glue"
#           ]
#         }
#       ]
#     }
#   ],
#   "environments": [
#     {
#       "settings": [
#         {
#           "platform_name": "AWS",
#           "platform_id": "8e99f3e5-5c12-4800-9c21-42cb429f20b3",
#         "account_id": "",
#
#           "services": [
#               {"service_name": "Glue",
#               "service_id": "c62a7401-23d9-4dd6-9885-f5b8f5cf760b",
#               "configs": [
#                 {
#                   "identifier": "glue",
#                   "database": "2",
#                   "account_id": "2",
#                   "kms_key": "2",
#                   "arn": "2"
#                 }]
#                },
#               {
#                   "service_name": "S3",
#               "service_id": "f503376c-fc49-40e3-8a3d-ee80804e0fe4",
#               "configs": [
#                 {
#                   "identifier": "s3",
#                   "bucket_name": "1",
#                   "arn": "1",
#                   "kms_key": "1"
#                 }
#               ]
#           ],
#
#         },
#       ],
#       "name": "test"
#     }
#   ]
# }
