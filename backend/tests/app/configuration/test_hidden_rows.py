from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import pytest
from sqlalchemy.orm import Session, object_session

from app.authorization.roles.schema import Scope
from app.configuration.domains.model import Domain
from app.configuration.domains.status import DomainStatus
from app.configuration.output_port_access_types.model import OutputPortAccessType
from app.core.authz import Action
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import UNFILTERED
from app.settings import settings
from tests.factories import (
    AccessModeFactory,
    DataProductFactory,
    DataProductSettingFactory,
    DataProductSettingValueFactory,
    DataProductTypeFactory,
    DomainFactory,
    GlobalRoleAssignmentFactory,
    LifecycleFactory,
    OutputPortAccessTypeFactory,
    OutputPortFactory,
    RoleFactory,
    TagFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.route_util import iter_app_routes

CONFIGURATION = "/api/v2/configuration"


@dataclass
class Hidden:
    data_product: DataProduct
    output_port: OutputPort
    technical_asset: TechnicalAsset


@dataclass
class Case:
    method: str
    path: str
    setup: Callable[[Hidden], dict]
    expected_status: int
    expected_detail: str | None = None
    body: dict | None = None
    check: Callable[[Session, Hidden, dict], None] = field(
        default=lambda session, hidden, params: None
    )


def _tag(_hidden: Hidden) -> dict:
    tag = TagFactory()
    data_product = DataProductFactory(
        visibility=DataProductVisibility.HIDDEN, tags=[tag]
    )
    OutputPortFactory(
        data_product=data_product,
        access_function=OutputPortAccessFunction.PRIVATE,
        tags=[tag],
    )
    TechnicalAssetFactory(owner=data_product, tags=[tag])
    return {"id": tag.id}


def _access_mode(hidden: Hidden) -> dict:
    access_mode = AccessModeFactory(
        technical_asset_types=["FakeLinkPlugin", "FakeTechnicalAssetConfiguration"]
    )
    hidden.technical_asset.access_modes = [access_mode]
    return {"id": access_mode.id}


def _access_type(hidden: Hidden) -> dict:
    OutputPortAccessTypeFactory(
        name="another", access_function=OutputPortAccessFunction.PRIVATE
    )
    return {"id": hidden.output_port.access_type_id}


def _lifecycle(hidden: Hidden) -> dict:
    lifecycle = LifecycleFactory()
    hidden.data_product.lifecycle = lifecycle
    hidden.output_port.lifecycle = lifecycle
    return {"id": lifecycle.id}


def _setting(hidden: Hidden) -> dict:
    setting = DataProductSettingFactory()
    DataProductSettingValueFactory(
        data_product=hidden.data_product, data_product_setting=setting
    )
    return {"id": setting.id}


def _data_product_type(hidden: Hidden) -> dict:
    return {"id": hidden.data_product.type_id}


def _data_product_type_migration(hidden: Hidden) -> dict:
    return {
        "from_id": hidden.data_product.type_id,
        "to_id": DataProductTypeFactory().id,
    }


def _domain(hidden: Hidden) -> dict:
    return {"id": hidden.data_product.domain_id}


def _domain_migration(hidden: Hidden) -> dict:
    return {"from_id": hidden.data_product.domain_id, "to_id": DomainFactory().id}


def _deleting_domain_with_finalizer(hidden: Hidden) -> dict:
    domain = DomainFactory(finalizers=["provisioner"])
    hidden.data_product.domain = domain
    object_session(domain).flush()
    domain.status = DomainStatus.DELETING
    return {"id": domain.id, "finalizer": "provisioner"}


def _moved(attribute: str) -> Callable[[Session, Hidden, dict], None]:
    def check(session: Session, hidden: Hidden, params: dict) -> None:
        data_product = session.get(
            DataProduct, hidden.data_product.id, execution_options=UNFILTERED
        )
        assert getattr(data_product, attribute) == params["to_id"]

    return check


def _lifecycle_cleared(session: Session, hidden: Hidden, params: dict) -> None:
    data_product = session.get(
        DataProduct, hidden.data_product.id, execution_options=UNFILTERED
    )
    output_port = session.get(
        OutputPort, hidden.output_port.id, execution_options=UNFILTERED
    )
    assert data_product is not None
    assert data_product.lifecycle_id is None
    assert output_port is not None
    assert output_port.lifecycle_id is None


def _domain_kept(session: Session, hidden: Hidden, params: dict) -> None:
    assert session.get(Domain, params["id"], execution_options=UNFILTERED)


def _access_type_still_invite_only(
    session: Session, hidden: Hidden, params: dict
) -> None:
    access_type = session.get(
        OutputPortAccessType, params["id"], execution_options=UNFILTERED
    )
    assert access_type.access_function == OutputPortAccessFunction.PRIVATE


CASES = [
    Case("DELETE", "/tags/{id}", _tag, 200),
    Case("PUT", "/tags/{id}", _tag, 200, body={"value": "renamed"}),
    Case("DELETE", "/access_modes/{id}", _access_mode, 400, "in use"),
    Case(
        "PUT",
        "/access_modes/{id}",
        _access_mode,
        400,
        "in use",
        body={"description": "x", "technical_asset_types": ["FakeLinkPlugin"]},
    ),
    Case("DELETE", "/output_port_access_types/{id}", _access_type, 400, "used by 1"),
    Case(
        "PUT",
        "/output_port_access_types/{id}",
        _access_type,
        400,
        "need an Access Type mapped to Invite only",
        body={
            "name": "renamed",
            "access_function": OutputPortAccessFunction.UNRESTRICTED.value,
        },
        check=_access_type_still_invite_only,
    ),
    Case(
        "DELETE",
        "/data_product_lifecycles/{id}",
        _lifecycle,
        200,
        check=_lifecycle_cleared,
    ),
    Case(
        "PUT",
        "/data_product_lifecycles/{id}",
        _lifecycle,
        200,
        body={"value": 1, "name": "renamed", "color": "red"},
    ),
    Case("DELETE", "/data_product_settings/{id}", _setting, 200),
    Case(
        "PUT",
        "/data_product_settings/{id}",
        _setting,
        200,
        body={
            "category": "x",
            "type": "checkbox",
            "tooltip": "x",
            "namespace": "renamed",
            "name": "renamed",
            "default": "True",
            "scope": "dataproduct",
        },
    ),
    Case(
        "DELETE",
        "/data_product_types/{id}",
        _data_product_type,
        400,
        "assigned to one or multiple data products",
    ),
    Case(
        "PUT",
        "/data_product_types/{id}",
        _data_product_type,
        200,
        body={"name": "renamed", "description": "x", "icon_key": "default"},
    ),
    Case(
        "PUT",
        "/data_product_types/migrate/{from_id}/{to_id}",
        _data_product_type_migration,
        200,
        check=_moved("type_id"),
    ),
    Case("DELETE", "/domains/{id}", _domain, 400, "still has data products"),
    Case(
        "PUT",
        "/domains/{id}",
        _domain,
        200,
        body={"name": "renamed", "description": "x"},
    ),
    Case(
        "PUT",
        "/domains/migrate/{from_id}/{to_id}",
        _domain_migration,
        200,
        check=_moved("domain_id"),
    ),
    Case(
        "DELETE",
        "/domains/{id}/finalizers/{finalizer}",
        _deleting_domain_with_finalizer,
        200,
        check=_domain_kept,
    ),
]
EXEMPT = {
    ("PUT", "/access_durations/{abstract_data_product_type}"): "no per-entity rows",
    ("PUT", "/theme_settings"): "no per-entity rows",
}


@pytest.fixture
def configuration_manager():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.GLOBAL,
        permissions=[
            Action.GLOBAL__UPDATE_CONFIGURATION,
            Action.GLOBAL__MANAGE_FINALIZERS,
        ],
    )
    GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)
    return user


@pytest.fixture
def hidden() -> Hidden:
    data_product = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    return Hidden(
        data_product=data_product,
        output_port=OutputPortFactory(
            data_product=data_product,
            access_function=OutputPortAccessFunction.PRIVATE,
        ),
        technical_asset=TechnicalAssetFactory(owner=data_product),
    )


def test_configuration_write__all_routes_covered():
    discovered = {
        (method, route.path.removeprefix(CONFIGURATION))
        for route in iter_app_routes()
        if route.path.startswith(CONFIGURATION)
        for method in route.methods & {"DELETE", "PUT"}
    }

    assert discovered == {(case.method, case.path) for case in CASES} | set(EXEMPT)


@pytest.mark.parametrize("admin", [False, True], ids=["manager", "admin"])
@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c.method} {c.path}")
def test_configuration_write__with_rows_hidden_from_user(
    case, admin, configuration_manager, hidden, client, session
):
    if admin:
        configuration_manager.admin_expiry = datetime(2099, 1, 1)
    params = case.setup(hidden)
    session.commit()  # noqa: allow-commit

    response = client.request(
        case.method,
        f"{CONFIGURATION}{case.path.format(**params)}",
        json=case.body,
    )

    assert response.status_code == case.expected_status, response.text
    if case.expected_detail:
        assert case.expected_detail in response.json()["detail"]
    session.expire_all()
    case.check(session, hidden, params)
