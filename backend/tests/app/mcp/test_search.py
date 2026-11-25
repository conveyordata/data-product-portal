import pytest
from fastapi import HTTPException
from fastmcp.exceptions import ToolError

from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.data_products.service import DataProductService
from app.mcp.details import (
    get_data_product_details,
    get_domain_details,
    get_output_port_details,
    get_technical_asset_details,
)
from app.mcp.search import search_data_products, universal_search
from app.settings import settings
from tests.app.mcp.test_permissions import call_mcp_tool
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DomainFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.session_util import as_user


def test_get_data_product_details(session):
    dp = DataProductFactory()
    user = UserFactory()
    with as_user(session, user.id):
        result = get_data_product_details(data_product_id=str(dp.id), db=session)
    assert result["id"] == dp.id


def test_get_output_port_details(session):
    ds = OutputPortFactory()
    user = UserFactory()
    with as_user(session, user.id):
        result = get_output_port_details(output_port_id=str(ds.id), db=session)
    assert result["id"] == ds.id


def test_get_technical_asset_details(session):
    ta = TechnicalAssetFactory()
    user = UserFactory()
    with as_user(session, user.id):
        result = get_technical_asset_details(technical_asset_id=str(ta.id), db=session)
    assert result["id"] == ta.id


def test_get_domain_details(session):
    domain = DomainFactory()
    user = UserFactory()
    with as_user(session, user.id):
        result = get_domain_details(domain_id=str(domain.id), db=session)
    assert result["id"] == domain.id


def test_search_data_products(session):
    churn = DataProductFactory(name="Customer Churn", description="Churn predictions")
    inventory = DataProductFactory(
        name="Warehouse Inventory", description="Stock levels per warehouse"
    )

    with as_user(session, UserFactory().id):
        DataProductService(session).recalculate_search(churn.id)
        DataProductService(session).recalculate_search(inventory.id)
        result = search_data_products(query="churn", db=session)

    assert [dp["id"] for dp in result["data_products"]] == [churn.id, inventory.id]


def test_search_data_products__lists_output_ports(session):
    output_port = OutputPortFactory()

    with as_user(session, UserFactory().id):
        result = search_data_products(db=session)

    [data_product] = result["data_products"]
    assert data_product["id"] == output_port.data_product_id
    assert [op["id"] for op in data_product["output_ports"]] == [output_port.id]


def test_search_data_products_no_query(session):
    DataProductFactory()
    DataProductFactory()

    user = UserFactory()
    with as_user(session, user.id):
        result = search_data_products(query=None, db=session)

    assert "data_products" in result
    assert result["count"] >= 2


def test_search_data_products_limit(session):
    for _ in range(5):
        DataProductFactory()

    user = UserFactory()
    with as_user(session, user.id):
        result = search_data_products(query=None, limit=2, db=session)

    assert result["count"] <= 2
    assert len(result["data_products"]) <= 2


@pytest.mark.parametrize("limit", [-1, 1001])
def test_search_data_products__rejects_invalid_limit(session, limit):
    with pytest.raises(ToolError, match="validation error"):
        call_mcp_tool("search_data_products", {"limit": limit})


def test_search_data_products_filters_applied(session):
    user = UserFactory()
    with as_user(session, user.id):
        result = search_data_products(query="test", db=session)

    assert result["filters_applied"] == {"query": "test"}


def test_search_data_products__filters_out_hidden(session):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    dp1 = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[AuthorizationAction.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
    )
    DataProductRoleAssignmentFactory(data_product=dp1, identity=user, role=role)
    with as_user(session, user.id):
        result = search_data_products(db=session)

    assert len(result["data_products"]) == 1
    assert result["data_products"][0]["id"] == dp1.id


def test_search_data_products_matches_description(session):
    dp = DataProductFactory(
        name="IrrelevantName", description="Customers cancelling their subscription"
    )
    other = DataProductFactory(name="OtherProduct", description="Stock per warehouse")

    with as_user(session, UserFactory().id):
        DataProductService(session).recalculate_search(dp.id)
        DataProductService(session).recalculate_search(other.id)
        result = search_data_products(query="subscription cancellations", db=session)

    assert result["data_products"][0]["id"] == dp.id


def test_universal_search(session):
    dp = DataProductFactory(name="IrrelevantName", description="unique_needle_xyz")

    user = UserFactory()
    with as_user(session, user.id):
        result = universal_search(query="", db=session)
    assert result["total_count"] == 2
    assert dp.id == result["results"]["data_products"][0]["id"]
    assert dp.domain.id == result["results"]["domains"][0]["id"]


def test_universal_search__output_ports(session):
    output_port = OutputPortFactory(name="needle port")
    OutputPortFactory(name="other port")

    with as_user(session, UserFactory().id):
        result = universal_search(
            query="needle", entity_types=["output_ports"], db=session
        )

    assert [op["id"] for op in result["results"]["output_ports"]] == [output_port.id]


def test_get_technical_asset_details__hidden_data_product_without_access(session):
    asset = TechnicalAssetFactory(
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    )

    with (
        as_user(session, UserFactory().id),
        pytest.raises(HTTPException, match="Technical asset not found"),
    ):
        get_technical_asset_details(technical_asset_id=str(asset.id), db=session)


@pytest.mark.parametrize(
    ("query", "expected_names"), [("needle", ["needle visible"]), ("zzz", [])]
)
def test_universal_search__technical_asset_of_hidden_data_product(
    session, query, expected_names
):
    TechnicalAssetFactory(name="needle visible")
    TechnicalAssetFactory(
        name="needle hidden",
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN),
    )

    with as_user(session, UserFactory().id):
        result = universal_search(
            query=query, entity_types=["technical_assets"], db=session
        )

    assert [
        asset.name for asset in result["results"]["technical_assets"]
    ] == expected_names
