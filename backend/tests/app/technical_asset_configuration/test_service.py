from typing import ClassVar

import pytest
from fastapi import HTTPException

from app.technical_asset_configuration.service import PluginService
from tests.fixtures.fake_plugin.schema import FakeLinkPlugin

CLOUD_CHILD = FakeLinkPlugin.get_platform_metadata().model_copy(
    update={"parent_platform": "cloud"}
)


class SharedUrlA(FakeLinkPlugin):
    name: ClassVar[str] = "SharedUrlA"
    _platform_metadata = CLOUD_CHILD


class SharedUrlB(FakeLinkPlugin):
    name: ClassVar[str] = "SharedUrlB"
    _platform_metadata = CLOUD_CHILD


class OtherUrl(FakeLinkPlugin):
    name: ClassVar[str] = "OtherUrl"
    _platform_metadata = CLOUD_CHILD

    @classmethod
    def get_url(cls, id, db, actor, environment=None) -> str:
        return "other"


def test_parent_platform_url_plugin__names_every_child_with_a_url():
    with pytest.raises(HTTPException) as error:
        PluginService._parent_platform_url_plugin(
            "cloud", [SharedUrlA, SharedUrlB, OtherUrl]
        )

    assert "(OtherUrl, SharedUrlA, SharedUrlB)" in error.value.detail
