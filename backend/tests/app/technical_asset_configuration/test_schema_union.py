import pytest
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

from app.settings import settings
from app.technical_asset_configuration.schema_union import DataOutputConfiguration


class Holder(BaseModel):
    configuration: DataOutputConfiguration


FAKE_CONFIGURATION = {
    "name": "FakeTechnicalAssetConfiguration",
    "path": "some/path",
    "granular": False,
    "table": "",
}


def test_resolve_configuration__builds_the_plugin_named_by_name():
    holder = Holder(configuration=FAKE_CONFIGURATION)

    assert holder.configuration.name == "FakeTechnicalAssetConfiguration"
    assert holder.configuration.path == "some/path"


def test_resolve_configuration__round_trips_unchanged():
    assert Holder(configuration=FAKE_CONFIGURATION).model_dump()["configuration"] == (
        FAKE_CONFIGURATION
    )


def test_resolve_configuration__rejects_a_missing_name():
    with pytest.raises(ValidationError, match="name is required"):
        Holder(configuration={"path": "some/path"})


def test_resolve_configuration__rejects_an_unknown_name():
    with pytest.raises(HTTPException) as exc_info:
        Holder(configuration={"name": "NoSuchPlugin"})

    assert exc_info.value.status_code == 400


def test_resolve_configuration__still_resolves_a_plugin_that_is_not_enabled(
    monkeypatch,
):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", [])
    holder = Holder(configuration=FAKE_CONFIGURATION)
    assert holder.configuration.name == "FakeTechnicalAssetConfiguration"


def test_resolve_configuration__rejects_a_plugin_that_has_no_configuration():
    with pytest.raises(HTTPException) as exc_info:
        Holder(configuration={"name": "FakeLinkPlugin"})

    assert exc_info.value.status_code == 400
    assert "no configuration of its own" in exc_info.value.detail
