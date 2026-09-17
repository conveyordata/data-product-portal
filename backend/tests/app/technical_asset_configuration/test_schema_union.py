import pytest
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

from app.settings import settings
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class Holder(BaseModel):
    configuration: DataOutputConfiguration


S3_CONFIGURATION = {
    "configuration_type": "S3TechnicalAssetConfiguration",
    "bucket": "some-bucket",
    "suffix": "",
    "path": "some/path",
}


def test_resolve_configuration__builds_the_plugin_named_by_configuration_type():
    holder = Holder(configuration=S3_CONFIGURATION)

    assert holder.configuration.name == "S3TechnicalAssetConfiguration"
    assert holder.configuration.bucket == "some-bucket"


def test_resolve_configuration__round_trips_unchanged():
    assert Holder(configuration=S3_CONFIGURATION).model_dump()["configuration"] == (
        S3_CONFIGURATION
    )


def test_resolve_configuration__rejects_a_missing_configuration_type():
    with pytest.raises(ValidationError, match="configuration_type is required"):
        Holder(configuration={"bucket": "some-bucket"})


def test_resolve_configuration__rejects_an_unknown_configuration_type():
    with pytest.raises(HTTPException) as exc_info:
        Holder(configuration={"configuration_type": "NoSuchPlugin"})

    assert exc_info.value.status_code == 400


def test_resolve_configuration__still_resolves_a_plugin_that_is_not_enabled(
    monkeypatch,
):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", [])
    holder = Holder(configuration=S3_CONFIGURATION)
    assert holder.configuration.name == "S3TechnicalAssetConfiguration"


def test_resolve_configuration__rejects_a_plugin_that_has_no_configuration():
    with pytest.raises(HTTPException) as exc_info:
        Holder(configuration={"configuration_type": "GitHubPlugin"})

    assert exc_info.value.status_code == 400
    assert "no configuration of its own" in exc_info.value.detail
