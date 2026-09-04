# ruff: noqa: S311, S105
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text  # noqa: TID251
from sqlalchemy.orm import Session
from starlette.routing import _DefaultLifespan

from app.authorization.roles.model import Role
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.service import AuthorizationService
from app.core.auth.device_flows.service import verify_auth_header
from app.core.authz import Action
from app.core.authz.authorization import Authorization
from app.core.context import _pending_events
from app.core.webhooks.events import V2Event
from app.data_products.output_ports.enums import OutputPortAccessType
from app.database.database import Base, get_system_db_session
from app.main import app
from app.settings import settings
from tests.factories import reset_unique_fakers
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_global import GlobalRoleAssignmentFactory

from . import TestingSessionLocal
from .factories.data_product_type import DataProductTypeFactory
from .factories.domain import DomainFactory
from .factories.user import UserFactory


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():
    from app.db_tool import init  # noqa: E402

    init(force=True, seed_path=None)
    return


def override_unauthenticated_get_db():
    test_db = None
    try:
        test_db = TestingSessionLocal()
        yield test_db
        test_db.commit()  # noqa: allow-commit
    finally:
        if test_db:
            test_db.close()


session = pytest.fixture(override_unauthenticated_get_db)

from app.core.auth import jwt  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def mock_oidc_config():
    """Mock OIDCConfiguration globally before any test runs."""
    mock_instance = MagicMock()
    mock_instance.client_id = "test_client_id"
    mock_instance.client_secret = "test_client_secret"
    mock_instance.redirect_uri = "http://test-redirect-uri"
    mock_instance.token_endpoint = "http://test-token-endpoint"
    mock_instance.authorization_endpoint = "http://test-authorization-endpoint"
    mock_instance.provider.name = "test-provider"
    # Force override the existing instance in `jwt.py`
    jwt.oidc = mock_instance


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # Disable lifespan for testing
    app.router.lifespan_context = _DefaultLifespan(app.router)

    app.dependency_overrides[get_system_db_session] = override_unauthenticated_get_db
    app.dependency_overrides[verify_auth_header] = lambda: "test"

    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()


@pytest.fixture
def everyone_role_permissions(session: Session):
    def everyone_role() -> Role:
        role = session.scalar(
            select(Role)
            .where(Role.prototype == Prototype.EVERYONE)
            .where(Role.scope == Scope.GLOBAL)
        )
        assert role is not None, "Failed to find the global 'everyone' role"
        return role

    @contextmanager
    def _change_permissions(*, permissions: list[Action] | None = None):
        role = everyone_role()
        if permissions is None:
            raise Exception("Permissions must be provided")

        original_permissions = list(role.permissions or [])
        next_permissions = [int(action) for action in permissions]

        role.permissions = next_permissions
        Authorization().sync_everyone_role_permissions(actions=permissions)

        try:
            yield
        finally:
            role = everyone_role()
            assert role is not None, "Failed to find the global 'everyone' role"
            role.permissions = original_permissions
            Authorization().sync_everyone_role_permissions(actions=original_permissions)

    return _change_permissions


@pytest.fixture
def default_data_product_payload() -> dict[str, Any]:
    data_product_type = DataProductTypeFactory()
    user = UserFactory()
    domain = DomainFactory()
    return {
        "name": "Test Data Product",
        "description": "Test Description",
        "namespace": "test-data_product",
        "tags": [],
        "type_id": str(data_product_type.id),
        "owners": [str(user.id)],
        "domain_id": str(domain.id),
    }


@pytest.fixture
def default_dataset_payload() -> dict[str, Any]:
    user = UserFactory()
    domain = DomainFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "namespace": "test-dataset",
        "tags": [],
        "owners": [str(user.id)],
        "access_type": OutputPortAccessType.RESTRICTED,
        "domain_id": str(domain.id),
    }


@pytest.fixture(autouse=True)
def clear_db(session: Session) -> None:
    """Clear database after each test."""
    truncate_tables = [
        table
        for table in Base.metadata.tables
        if table not in {"casbin_rule", "roles", "alembic_version"}
    ]
    session.execute(text(f"TRUNCATE TABLE {', '.join(truncate_tables)}"))
    roles_table = Base.metadata.tables.get("roles")
    if roles_table is not None:
        session.execute(roles_table.delete().where(roles_table.c.prototype == 0))
    AuthorizationService(session).reload_enforcer()
    # TODO fix by using factory for device token test
    # Device token test is broken without this
    session.commit()  # noqa: allow-commit
    reset_unique_fakers()


@pytest.fixture
def admin() -> UserFactory:
    role = RoleFactory.admin()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
    return user


@pytest.fixture
def authorizer() -> Authorization:
    return Authorization()


@contextmanager
def webhook_v2_config(url: str | None = "http://test-v2.example.com/hook"):
    original = settings.WEBHOOK_V2_URL
    settings.WEBHOOK_V2_URL = url
    try:
        yield
    finally:
        settings.WEBHOOK_V2_URL = original


@contextmanager
def webhook_v2_input_port_events_from_technical_asset_output_port_link(
    enabled: bool = True,
):
    original = (
        settings.WEBHOOK_V2_TECHNICAL_ASSET_OUTPUT_PORT_LINKS_TRIGGER_INPUT_PORT_EVENTS
    )
    settings.WEBHOOK_V2_TECHNICAL_ASSET_OUTPUT_PORT_LINKS_TRIGGER_INPUT_PORT_EVENTS = (
        enabled
    )
    try:
        yield
    finally:
        settings.WEBHOOK_V2_TECHNICAL_ASSET_OUTPUT_PORT_LINKS_TRIGGER_INPUT_PORT_EVENTS = original


class CapturedEventsMock:
    def __init__(self) -> None:
        self.captured_events: list[V2Event] = []

    def record(self, event: V2Event) -> None:
        self.captured_events.append(event)


@pytest.fixture
def capture_events() -> Iterator["CapturedEventsMock"]:
    mock = CapturedEventsMock()

    def _queue_event(event: V2Event) -> None:
        if _pending_events.get() is None or not settings.WEBHOOK_V2_URL:
            return
        mock.record(event)

    def _queue_events(events: list[V2Event]) -> None:
        if _pending_events.get() is None or not settings.WEBHOOK_V2_URL:
            return
        for event in events:
            mock.record(event)

    with (
        patch("app.core.context.queue_event", side_effect=_queue_event),
        patch("app.core.context.queue_events", side_effect=_queue_events),
        patch("app.database.event_mixin.queue_events", side_effect=_queue_events),
        webhook_v2_config(),
    ):
        yield mock
