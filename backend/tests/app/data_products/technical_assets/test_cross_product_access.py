from uuid import UUID

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.settings import settings
from tests.app.shared.test_router import _iter_app_routes
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)

ASSETS = "/api/v2/data_products/{data_product_id}/technical_assets"
ASSET = f"{ASSETS}/{{id}}"
LINK = "/api/v2/data_products/{data_product_id}/output_ports/{output_port_id}/technical_assets"


def _link_request_body(technical_asset_id: UUID) -> dict[str, str]:
    return {"technical_asset_id": str(technical_asset_id)}


ROUTES = [
    ("GET", ASSET, lambda _: None),
    ("GET", f"{ASSET}/history", lambda _: None),
    ("GET", f"{ASSET}/graph", lambda _: None),
    ("PUT", ASSET, lambda _: {"name": "x", "description": "x", "tag_ids": []}),
    ("PUT", f"{ASSET}/status", lambda _: {"status": "pending"}),
    ("DELETE", ASSET, lambda _: None),
    ("POST", f"{LINK}/add", _link_request_body),
    ("DELETE", f"{LINK}/remove", _link_request_body),
    ("POST", f"{LINK}/approve_link_request", _link_request_body),
    ("POST", f"{LINK}/deny_link_request", _link_request_body),
]
ROUTES_WITHOUT_TECHNICAL_ASSET_ID = {("GET", f"{ASSETS}/"), ("POST", f"{ASSETS}/")}


def test_technical_asset_route__all_routes_covered():
    discovered = {
        (method, route.path)
        for route in _iter_app_routes()
        if _is_technical_asset_route(route)
        for method in route.methods
    }

    assert (
        discovered
        == {(method, path) for method, path, _ in ROUTES}
        | ROUTES_WITHOUT_TECHNICAL_ASSET_ID
    )


@pytest.mark.parametrize(("method", "path", "make_body"), ROUTES)
def test_technical_asset_route__asset_of_other_data_product(
    method, path, make_body, client, session: Session
):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    my_data_product = DataProductFactory()
    my_output_port = OutputPortFactory(data_product=my_data_product)
    DataProductRoleAssignmentFactory(
        identity_id=user.id,
        data_product_id=my_data_product.id,
        role_id=RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.HIDDEN__DATA_PRODUCT__READ,
                Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
                Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET,
                Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        ).id,
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id,
        output_port=my_output_port,
        role_id=RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        ).id,
    )
    asset = TechnicalAssetFactory(owner=DataProductFactory())
    # The API never links a port to another data product's asset; this link only
    # gives remove/approve/deny something to wrongly act on.
    link = TechnicalAssetOutputPortAssociationFactory(
        technical_asset=asset, output_port=my_output_port, status=DecisionStatus.PENDING
    )
    before = (asset.name, asset.description, asset.status)

    response = client.request(
        method,
        path.format(
            data_product_id=my_data_product.id,
            output_port_id=my_output_port.id,
            id=asset.id,
        ),
        json=make_body(asset.id),
    )

    assert response.status_code == 404, response.text
    session.expire_all()
    asset = session.get(TechnicalAsset, asset.id)
    assert asset is not None
    assert (asset.name, asset.description, asset.status) == before
    assert (
        session.get(TechnicalAssetOutputPortAssociation, link.id).status
        == DecisionStatus.PENDING
    )
    assert (
        session.scalar(
            select(func.count()).where(
                TechnicalAssetOutputPortAssociation.technical_asset_id == asset.id
            )
        )
        == 1
    )


def _is_technical_asset_route(route) -> bool:
    dependant = getattr(route, "original_route", route).dependant
    body_fields = {
        name
        for param in dependant.body_params
        for name in getattr(param.field_info.annotation, "model_fields", {})
    }
    # ponytail: a technical_asset_id nested deeper in a body is not discovered.
    return (
        route.path.startswith((ASSETS, LINK))
        or "technical_asset_id"
        in {param.name for param in dependant.path_params + dependant.query_params}
        | body_fields
    )
