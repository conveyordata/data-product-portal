import json
import uuid
from pathlib import Path

import pytest

from example import provisioner as prov_module
from example.provisioner import FINALIZER_NAME, ExplorationProvisioner
from sdk import Client, ReconcileManager
from sdk.api_client.models import (
    Domain,
    Exploration,
    GetExplorationResponse,
    GetExplorationsResponse,
    User,
)
from sdk.api_client.models.abstract_data_product_status import AbstractDataProductStatus


def _fake_exploration(
    exploration_id: uuid.UUID,
    status: AbstractDataProductStatus = AbstractDataProductStatus.ACTIVE,
    finalizers: list[str] | None = None,
) -> GetExplorationResponse:
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
        status=status,
        finalizers=finalizers if finalizers is not None else [],
    )


@pytest.fixture
def fake_client() -> Client:
    # Never actually used: get_exploration.asyncio is patched out.
    return Client(base_url="http://portal.invalid")


@pytest.fixture
def patch_get_exploration(monkeypatch):
    """Patch the portal lookup; returns a setter for the value reconcile will see."""
    state: dict[uuid.UUID, GetExplorationResponse] = {}

    async def fake_get(id, client):  # noqa: A002 - matches generated signature
        return state.get(id)

    monkeypatch.setattr(prov_module.get_exploration, "asyncio", fake_get)

    def set_exploration(exploration_id, value: GetExplorationResponse):
        state[exploration_id] = value

    return set_exploration


@pytest.fixture
def patch_add_finalizer(monkeypatch):
    """Capture calls to add_exploration_finalizer.asyncio."""
    calls: list[dict] = []

    async def fake_add(id, client, body):  # noqa: A002
        calls.append({"id": id, "finalizer": body.finalizer})

    monkeypatch.setattr(prov_module.add_exploration_finalizer, "asyncio", fake_add)
    return calls


@pytest.fixture
def patch_remove_finalizer(monkeypatch):
    """Capture calls to remove_exploration_finalizer.asyncio."""
    calls: list[dict] = []

    async def fake_remove(id, finalizer, client):  # noqa: A002
        calls.append({"id": id, "finalizer": finalizer})

    monkeypatch.setattr(
        prov_module.remove_exploration_finalizer, "asyncio", fake_remove
    )
    return calls


async def test_reconcile_provisions_manifest(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
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
    # Finalizer must be registered before provisioning.
    assert patch_add_finalizer == [{"id": eid, "finalizer": FINALIZER_NAME}]
    assert patch_remove_finalizer == []


async def test_reconcile_is_idempotent(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(eid)
    await provisioner.reconcile(eid)  # second pass must not error

    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()
    # add_finalizer is called each time (the portal call itself is idempotent).
    assert len(patch_add_finalizer) == 2
    assert patch_remove_finalizer == []


async def test_reconcile_reflects_updated_state(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
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
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(eid)
    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()

    # Portal now reports the exploration is fully gone (hard-deleted / 404).
    patch_get_exploration(eid, None)
    await provisioner.reconcile(eid)

    assert not manifest.exists()
    assert not manifest.parent.exists()
    # No finalizer removal for the hard-delete path — exploration is already gone.
    assert patch_remove_finalizer == []


async def test_reconcile_deprovision_when_already_absent(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, None)
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    # Must be a no-op, not raise.
    result = await provisioner.reconcile(eid)

    assert result is None
    assert not (tmp_path / str(eid)).exists()
    assert patch_add_finalizer == []
    assert patch_remove_finalizer == []


async def test_reconcile_deleting_deprovisions_and_releases_finalizer(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    """When the exploration is DELETING, deprovision locally then release the finalizer."""
    eid = uuid.uuid4()
    # First reconcile while ACTIVE — sets up the workspace.
    patch_get_exploration(
        eid, _fake_exploration(eid, status=AbstractDataProductStatus.ACTIVE)
    )
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)
    await provisioner.reconcile(eid)

    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()

    # Portal transitions the exploration to DELETING.
    patch_get_exploration(
        eid,
        _fake_exploration(
            eid, status=AbstractDataProductStatus.DELETING, finalizers=[FINALIZER_NAME]
        ),
    )
    await provisioner.reconcile(eid)

    # Workspace must be cleaned up.
    assert not manifest.exists()
    assert not manifest.parent.exists()
    # Finalizer must be released so the portal can hard-delete.
    assert patch_remove_finalizer == [{"id": eid, "finalizer": FINALIZER_NAME}]
    # No extra add_finalizer call during the DELETING reconcile.
    assert len(patch_add_finalizer) == 1  # only the initial ACTIVE reconcile


async def test_reconcile_deleting_already_absent_releases_finalizer(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    """DELETING reconcile releases the finalizer even if the workspace was already gone."""
    eid = uuid.uuid4()
    patch_get_exploration(
        eid,
        _fake_exploration(
            eid, status=AbstractDataProductStatus.DELETING, finalizers=[FINALIZER_NAME]
        ),
    )
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    result = await provisioner.reconcile(eid)

    assert result is None
    assert not (tmp_path / str(eid)).exists()
    assert patch_remove_finalizer == [{"id": eid, "finalizer": FINALIZER_NAME}]
    assert patch_add_finalizer == []


async def test_reconcile_deleting_without_our_finalizer_is_noop(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    """If our finalizer is absent when DELETING, we have already cleaned up — skip."""
    eid = uuid.uuid4()
    patch_get_exploration(
        eid,
        _fake_exploration(
            eid, status=AbstractDataProductStatus.DELETING, finalizers=[]
        ),
    )
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    result = await provisioner.reconcile(eid)

    assert result is None
    assert patch_remove_finalizer == []
    assert patch_add_finalizer == []


async def test_reconcile_runs_via_manager(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)
    manager = ReconcileManager(provisioner, default_delay=0.0, num_workers=2)
    manager.start()

    # Multiple events for the same exploration should coalesce into a single manifest.
    await manager.enqueue(eid)
    await manager.enqueue(eid)

    manifest = tmp_path / str(eid) / "manifest.json"
    import asyncio

    for _ in range(200):
        if manifest.exists():
            break
        await asyncio.sleep(0.01)
    await manager.stop()

    assert manifest.exists()
