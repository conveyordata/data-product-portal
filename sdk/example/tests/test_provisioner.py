import json
import uuid
from http import HTTPStatus
from pathlib import Path

import pytest

from example import provisioner as prov_module
from example.provisioner import (
    FINALIZER_NAME,
    DomainProvisioner,
    ExplorationProvisioner,
)
from sdk import Client
from sdk.api_client.types import Response
from sdk.api_client.models import (
    Domain,
    DomainStatus,
    GetDomainResponse,
    GetExplorationResponse,
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
        domain=Domain(
            name="my-domain", namespace="my-domain", id=uuid.uuid4(), description="desc"
        ),
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
    state: dict[uuid.UUID, GetExplorationResponse | HTTPStatus | None] = {}

    async def fake_get(id, client):  # noqa: A002 - matches generated signature
        value = state.get(id)
        if isinstance(value, HTTPStatus):
            return Response(status_code=value, content=b"", headers={}, parsed=None)
        if value is None:
            return Response(
                status_code=HTTPStatus.NOT_FOUND, content=b"", headers={}, parsed=None
            )
        return Response(
            status_code=HTTPStatus.OK, content=b"", headers={}, parsed=value
        )

    monkeypatch.setattr(prov_module.get_exploration, "asyncio_detailed", fake_get)

    def set_exploration(
        exploration_id, value: GetExplorationResponse | HTTPStatus | None
    ):
        state[exploration_id] = value

    return set_exploration


@pytest.fixture
def patch_add_finalizer(monkeypatch):
    """Capture calls to add_exploration_finalizer.asyncio_detailed."""
    calls: list[dict] = []

    async def fake_add(id, client, body):  # noqa: A002
        calls.append({"id": id, "finalizer": body.finalizer})
        return Response(status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None)

    monkeypatch.setattr(
        prov_module.add_exploration_finalizer, "asyncio_detailed", fake_add
    )
    return calls


@pytest.fixture
def patch_remove_finalizer(monkeypatch):
    """Capture calls to remove_exploration_finalizer.asyncio_detailed."""
    calls: list[dict] = []

    async def fake_remove(id, finalizer, client):  # noqa: A002
        calls.append({"id": id, "finalizer": finalizer})
        return Response(status_code=HTTPStatus.OK, content=b"", headers={}, parsed=None)

    monkeypatch.setattr(
        prov_module.remove_exploration_finalizer, "asyncio_detailed", fake_remove
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


async def test_reconcile_404_after_deleting_is_noop(
    tmp_path: Path,
    fake_client,
    patch_get_exploration,
    patch_add_finalizer,
    patch_remove_finalizer,
):
    """A 404 after the DELETING path has already cleaned up is a no-op.

    Because we register the finalizer before provisioning, the portal can only
    hard-delete after we have deprovisioned and released our finalizer via the
    DELETING path. By the time we see a 404 the manifest is already gone.
    """
    eid = uuid.uuid4()
    # First provision.
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)
    await provisioner.reconcile(eid)
    manifest = tmp_path / str(eid) / "manifest.json"
    assert manifest.exists()

    # Simulate DELETING path: we deprovision and release the finalizer.
    patch_get_exploration(
        eid,
        _fake_exploration(
            eid, status=AbstractDataProductStatus.DELETING, finalizers=[FINALIZER_NAME]
        ),
    )
    await provisioner.reconcile(eid)
    assert not manifest.exists()

    # Now the portal hard-deletes (404). Must be a no-op — nothing left to clean up.
    patch_get_exploration(eid, None)
    await provisioner.reconcile(eid)

    assert not (tmp_path / str(eid)).exists()
    assert patch_remove_finalizer == [{"id": eid, "finalizer": FINALIZER_NAME}]


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


def _fake_domain(
    domain_id: uuid.UUID, status: DomainStatus, finalizers: list[str]
) -> GetDomainResponse:
    return GetDomainResponse(
        id=domain_id,
        name="Finance",
        namespace="finance",
        description="desc",
        status=status,
        finalizers=finalizers,
    )


@pytest.fixture
def patch_domain_api(monkeypatch):
    """Patch the domain endpoints; returns the state and recorded calls."""
    calls: dict = {
        "state": {},
        "get_status": None,
        "add_status": HTTPStatus.OK,
        "remove_status": HTTPStatus.OK,
        "added": [],
        "removed": [],
    }

    async def fake_get(id, client):  # noqa: A002
        domain = calls["state"].get(id)
        status = calls["get_status"] or (
            HTTPStatus.OK if domain else HTTPStatus.NOT_FOUND
        )
        parsed = domain if status == HTTPStatus.OK else None
        return Response(status_code=status, content=b"", headers={}, parsed=parsed)

    async def fake_add(id, client, body):  # noqa: A002
        calls["added"].append(id)
        return Response(
            status_code=calls["add_status"], content=b"", headers={}, parsed=None
        )

    async def fake_remove(id, finalizer, client):  # noqa: A002
        calls["removed"].append(id)
        return Response(
            status_code=calls["remove_status"], content=b"", headers={}, parsed=None
        )

    monkeypatch.setattr(prov_module.get_domain, "asyncio_detailed", fake_get)
    monkeypatch.setattr(prov_module.add_domain_finalizer, "asyncio_detailed", fake_add)
    monkeypatch.setattr(
        prov_module.remove_domain_finalizer, "asyncio_detailed", fake_remove
    )
    return calls


async def test_domain_reconcile_provisions_then_deprovisions(
    tmp_path: Path, fake_client, patch_domain_api
):
    did = uuid.uuid4()
    state = patch_domain_api["state"]
    added = patch_domain_api["added"]
    removed = patch_domain_api["removed"]

    def domain(status: DomainStatus, finalizers: list[str]) -> GetDomainResponse:
        return _fake_domain(did, status, finalizers)

    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)
    state[did] = domain(DomainStatus.ACTIVE, [])
    await provisioner.reconcile(did)

    manifest = tmp_path / "domains" / "finance" / "manifest.json"
    assert json.loads(manifest.read_text())["namespace"] == "finance"
    assert added == [did]

    state[did] = domain(DomainStatus.DELETING, [FINALIZER_NAME])
    await provisioner.reconcile(did)

    assert not manifest.parent.exists()
    assert removed == [did]


async def test_domain_reconcile_does_not_provision_without_finalizer(
    tmp_path: Path, fake_client, patch_domain_api
):
    did = uuid.uuid4()
    patch_domain_api["state"][did] = _fake_domain(did, DomainStatus.ACTIVE, [])
    patch_domain_api["add_status"] = HTTPStatus.CONFLICT
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not add finalizer"):
        await provisioner.reconcile(did)

    assert not (tmp_path / "domains" / "finance").exists()


async def test_domain_deprovision_tolerates_extra_files(
    tmp_path: Path, fake_client, patch_domain_api
):
    did = uuid.uuid4()
    domain_dir = tmp_path / "domains" / "finance"
    domain_dir.mkdir(parents=True)
    (domain_dir / "other.txt").write_text("keep")
    patch_domain_api["state"][did] = _fake_domain(
        did, DomainStatus.DELETING, [FINALIZER_NAME]
    )
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(did)

    assert patch_domain_api["removed"] == [did]


async def test_domain_reconcile_fails_when_finalizer_removal_fails(
    tmp_path: Path, fake_client, patch_domain_api
):
    did = uuid.uuid4()
    patch_domain_api["state"][did] = _fake_domain(
        did, DomainStatus.DELETING, [FINALIZER_NAME]
    )
    patch_domain_api["remove_status"] = HTTPStatus.BAD_REQUEST
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not remove finalizer"):
        await provisioner.reconcile(did)


async def test_domain_reconcile_deleted_domain_is_noop(
    tmp_path: Path, fake_client, patch_domain_api
):
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    await provisioner.reconcile(uuid.uuid4())

    assert patch_domain_api["added"] == []
    assert patch_domain_api["removed"] == []


@pytest.mark.parametrize(
    "status",
    [
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ],
)
async def test_domain_reconcile_failed_fetch_retries(
    tmp_path: Path, fake_client, patch_domain_api, status
):
    did = uuid.uuid4()
    patch_domain_api["state"][did] = _fake_domain(
        did, DomainStatus.DELETING, [FINALIZER_NAME]
    )
    patch_domain_api["get_status"] = status
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not fetch domain"):
        await provisioner.reconcile(did)

    assert patch_domain_api["removed"] == []


async def test_domain_list_ids_failed_listing_retries(
    tmp_path: Path, fake_client, monkeypatch
):
    async def fake_list(client):
        return None

    monkeypatch.setattr(prov_module.get_domains, "asyncio", fake_list)
    provisioner = DomainProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not list domains"):
        await provisioner.list_ids()


@pytest.mark.parametrize(
    "status",
    [
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ],
)
async def test_exploration_reconcile_failed_fetch_retries(
    tmp_path: Path, fake_client, patch_get_exploration, patch_remove_finalizer, status
):
    eid = uuid.uuid4()
    patch_get_exploration(eid, status)
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not fetch exploration"):
        await provisioner.reconcile(eid)

    assert patch_remove_finalizer == []


async def test_exploration_list_ids_failed_listing_retries(
    tmp_path: Path, fake_client, monkeypatch
):
    async def fake_list(client):
        return None

    monkeypatch.setattr(prov_module.get_explorations, "asyncio", fake_list)
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not list explorations"):
        await provisioner.list_ids()


async def test_exploration_reconcile_does_not_provision_without_finalizer(
    tmp_path: Path, fake_client, patch_get_exploration, monkeypatch
):
    async def fake_add(id, client, body):  # noqa: A002
        return Response(
            status_code=HTTPStatus.CONFLICT, content=b"", headers={}, parsed=None
        )

    monkeypatch.setattr(
        prov_module.add_exploration_finalizer, "asyncio_detailed", fake_add
    )
    eid = uuid.uuid4()
    patch_get_exploration(eid, _fake_exploration(eid))
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not add finalizer"):
        await provisioner.reconcile(eid)

    assert not (tmp_path / str(eid)).exists()


async def test_exploration_reconcile_fails_when_finalizer_removal_fails(
    tmp_path: Path, fake_client, patch_get_exploration, monkeypatch
):
    async def fake_remove(id, finalizer, client):  # noqa: A002
        return Response(
            status_code=HTTPStatus.BAD_REQUEST, content=b"", headers={}, parsed=None
        )

    monkeypatch.setattr(
        prov_module.remove_exploration_finalizer, "asyncio_detailed", fake_remove
    )
    eid = uuid.uuid4()
    patch_get_exploration(
        eid,
        _fake_exploration(
            eid, status=AbstractDataProductStatus.DELETING, finalizers=[FINALIZER_NAME]
        ),
    )
    provisioner = ExplorationProvisioner(client=fake_client, workspace=tmp_path)

    with pytest.raises(Exception, match="Could not remove finalizer"):
        await provisioner.reconcile(eid)
