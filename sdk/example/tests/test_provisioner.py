import json
import uuid
from pathlib import Path

import pytest

from example import provisioner as prov_module
from example.provisioner import ExplorationProvisioner
from sdk import Client
from sdk.api_client.models import (
    Domain,
    GetExplorationResponse,
    User,
)
from sdk.api_client.models.abstract_data_product_status import AbstractDataProductStatus


def _fake_exploration(exploration_id: uuid.UUID) -> GetExplorationResponse:
    return GetExplorationResponse(
        id=exploration_id,
        name="my-exploration",
        namespace="my-ns",
        description="a description",
        domain=Domain(name="my-domain", id=uuid.uuid4(), description="desc"),
        owner=User(
            email="owner@example.com",
            id=uuid.uuid4(),
            first_name="Stijn",
            last_name="De Haes",
            external_id="bla",
            has_seen_tour=False,
            can_become_admin=False,
        ),
        status=AbstractDataProductStatus.ACTIVE,
        finalizers=[],
    )


@pytest.fixture
def fake_client() -> Client:
    # Never actually used: get_exploration.asyncio is patched out.
    return Client(base_url="http://portal.invalid")


@pytest.fixture
def patch_get_exploration(
    monkeypatch,
):
    """Patch the portal lookup; returns a setter for the value reconcile will see."""
    state: dict[uuid.UUID, GetExplorationResponse] = {}

    async def fake_get(id, client):  # noqa: A002 - matches generated signature
        return state.get(id)

    monkeypatch.setattr(prov_module.get_exploration, "asyncio", fake_get)

    def set_exploration(exploration_id, value: GetExplorationResponse):
        state[exploration_id] = value

    return set_exploration


async def test_reconcile_provisions_manifest(
    tmp_path: Path, fake_client, patch_get_exploration
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    result = await provisioner.reconcile(eid)

    assert result is None
    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()
    data = json.loads(manifest.read_text())
    assert data == {
        "id": str(eid),
        "name": "my-exploration",
        "namespace": "my-ns",
        "description": "a description",
        "domain": "my-domain",
        "owner": "owner@example.com",
    }


async def test_reconcile_is_idempotent(
    tmp_path: Path, fake_client, patch_get_exploration
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(eid)
    await provisioner.reconcile(eid)  # second pass must not error

    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()


async def test_reconcile_reflects_updated_state(
    tmp_path: Path, fake_client, patch_get_exploration
):
    eid = uuid.uuid4()
    exploration = _fake_exploration(eid)
    patch_get_exploration(eid, exploration)
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(eid)

    exploration.name = "renamed-exploration"
    await provisioner.reconcile(eid)

    manifest = tmp_path / str(eid) / "manifest.json"
    assert json.loads(manifest.read_text())["name"] == "renamed-exploration"


async def test_reconcile_deprovisions_when_deleted(
    tmp_path: Path, fake_client, patch_get_exploration
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(eid)
    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()

    # Portal now reports the exploration is gone.
    patch_get_exploration(eid, None)
    await provisioner.reconcile(eid)

    assert not manifest.exists()
    assert not manifest.parent.exists()


async def test_reconcile_deprovision_when_already_absent(
    tmp_path: Path, fake_client, patch_get_exploration
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, None)
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    # Must be a no-op, not raise.
    result = await provisioner.reconcile(eid)

    assert result is None
    assert not (tmp_path / str(eid)).exists()
