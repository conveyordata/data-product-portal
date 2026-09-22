from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.data_products.output_ports.service import OutputPortService
from app.mcp.mcp import mcp
from tests.app.mcp.util import call_mcp_tool
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


def test_search_output_ports(session):
    user = UserFactory()
    ds1 = OutputPortFactory(name="Customer Data")
    ds2 = OutputPortFactory(name="Sales Data")
    with as_user(session, user.id):
        OutputPortService(db=session).recalculate_search_for_all_output_ports()
    result = call_mcp_tool(
        mcp, session, user, "search_output_ports", {"query": "Data"}
    ).data

    assert "output_ports" in result
    assert result["count"] >= 2
    returned_names = {op["name"] for op in result["output_ports"]}
    assert ds1.name in returned_names
    assert ds2.name in returned_names


def test_search_output_ports_no_query(session):
    user = UserFactory()
    OutputPortFactory(name="Customer Data")
    with as_user(session, user.id):
        OutputPortService(db=session).recalculate_search_for_all_output_ports()
    result = call_mcp_tool(mcp, session, user, "search_output_ports").data

    assert "output_ports" in result
    assert result["count"] == 1


def test_get_data_product_details(session):
    dp = DataProductFactory()
    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "get_data_product_details", {"data_product_id": str(dp.id)}
    ).data
    assert result["id"] == str(dp.id)


def test_get_output_port_details(session):
    ds = OutputPortFactory()
    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "get_output_port_details", {"output_port_id": str(ds.id)}
    ).data
    assert result["id"] == str(ds.id)


def test_get_technical_asset_details(session):
    ta = TechnicalAssetFactory()
    user = UserFactory()
    result = call_mcp_tool(
        mcp,
        session,
        user,
        "get_technical_asset_details",
        {"technical_asset_id": str(ta.id)},
    ).data
    assert result["id"] == str(ta.id)


def test_get_domain_details(session):
    domain = DomainFactory()
    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "get_domain_details", {"domain_id": str(domain.id)}
    ).data
    assert result["id"] == str(domain.id)


def test_search_data_products(session):
    dp1 = DataProductFactory(name="Alpha Product", description="alpha description")
    dp2 = DataProductFactory(name="Beta Product", description="beta description")

    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "search_data_products", {"query": "Alpha"}
    ).data

    assert "data_products" in result
    assert result["count"] == 1
    returned_names = {dp["name"] for dp in result["data_products"]}
    assert dp1.name in returned_names
    assert dp2.name not in returned_names


def test_search_data_products_no_query(session):
    DataProductFactory()
    DataProductFactory()

    user = UserFactory()
    result = call_mcp_tool(mcp, session, user, "search_data_products").data

    assert "data_products" in result
    assert result["count"] >= 2


def test_search_data_products_by_domain(session):
    domain = DomainFactory()
    dp_in_domain = DataProductFactory(domain=domain)
    DataProductFactory()

    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "search_data_products", {"domain_id": str(domain.id)}
    ).data

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert str(dp_in_domain.id) in returned_ids
    assert result["count"] == 1


def test_search_data_products_by_status(session):
    from app.data_products.status import AbstractDataProductStatus

    active_dp = DataProductFactory(status=AbstractDataProductStatus.ACTIVE.value)
    DataProductFactory(status=AbstractDataProductStatus.PENDING.value)

    user = UserFactory()
    result = call_mcp_tool(
        mcp,
        session,
        user,
        "search_data_products",
        {"status": AbstractDataProductStatus.ACTIVE.value},
    ).data

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert str(active_dp.id) in returned_ids
    for dp in result["data_products"]:
        assert dp["status"] == "active"


def test_search_data_products_limit(session):
    for _ in range(5):
        DataProductFactory()

    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "search_data_products", {"limit": 2}
    ).data

    assert result["count"] <= 2
    assert len(result["data_products"]) <= 2


def test_search_data_products_filters_applied(session):
    user = UserFactory()
    result = call_mcp_tool(
        mcp,
        session,
        user,
        "search_data_products",
        {"query": "test", "domain_id": None, "status": "active"},
    ).data

    assert result["filters_applied"]["query"] == "test"
    assert result["filters_applied"]["domain_id"] is None
    assert result["filters_applied"]["status"] == "active"


def test_search_data_products__filters_out_hidden(session):
    user = UserFactory()
    dp1 = DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    DataProductFactory(visibility=DataProductVisibility.HIDDEN)
    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[AuthorizationAction.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
    )
    DataProductRoleAssignmentFactory(data_product=dp1, user=user, role=role)
    result = call_mcp_tool(mcp, session, user, "search_data_products").data

    assert len(result["data_products"]) == 1
    assert result["data_products"][0]["id"] == str(dp1.id)


def test_search_data_products_matches_description(session):
    dp = DataProductFactory(name="IrrelevantName", description="unique_needle_xyz")
    DataProductFactory(name="OtherProduct", description="something else")

    user = UserFactory()
    result = call_mcp_tool(
        mcp, session, user, "search_data_products", {"query": "unique_needle_xyz"}
    ).data

    assert result["count"] == 1
    assert result["data_products"][0]["id"] == str(dp.id)


def test_universal_search(session):
    dp = DataProductFactory(name="IrrelevantName", description="unique_needle_xyz")

    user = UserFactory()
    result = call_mcp_tool(mcp, session, user, "universal_search", {"query": ""}).data
    assert result["total_count"] == 2
    assert str(dp.id) == result["results"]["data_products"][0]["id"]
    assert str(dp.domain.id) == result["results"]["domains"][0]["id"]
