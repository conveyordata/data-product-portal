from contextlib import contextmanager
from unittest.mock import Mock, patch

import pytest

from app.data_products.output_ports.service import OutputPortService
from app.mcp.mcp import (
    get_data_product_details,
    get_domain_details,
    get_output_port_details,
    get_technical_asset_details,
    search_data_products,
    search_output_ports,
)
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    DomainFactory,
    TechnicalAssetFactory,
)


@pytest.fixture
def mcp_mocks(session):
    mock_user = {
        "id": "00000000-0000-0000-0000-000000000001",
        "external_id": "test-user",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
    }
    mock_token = Mock()
    mock_token.token = "test-token"

    @contextmanager
    def mock_db():
        yield session

    @contextmanager
    def apply():
        with (
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.get_db_context", side_effect=lambda: mock_db()),
        ):
            yield

    return apply


def test_search_output_ports(session, mcp_mocks):
    ds1 = DatasetFactory(name="Customer Data")
    ds2 = DatasetFactory(name="Sales Data")
    OutputPortService(db=session).recalculate_search_for_all_output_ports()

    with mcp_mocks():
        result = search_output_ports(query="Data")

    assert "output_ports" in result
    assert result["count"] >= 2
    returned_names = {op["name"] for op in result["output_ports"]}
    assert ds1.name in returned_names
    assert ds2.name in returned_names


def test_search_output_ports_no_query(session, mcp_mocks):
    DatasetFactory(name="Customer Data")
    OutputPortService(db=session).recalculate_search_for_all_output_ports()

    with mcp_mocks():
        result = search_output_ports(query=None)

    assert "output_ports" in result
    assert result["count"] == 1


def test_get_data_product_details(mcp_mocks):
    dp = DataProductFactory()
    with mcp_mocks():
        result = get_data_product_details(data_product_id=str(dp.id))
    assert result["id"] == dp.id


def test_get_output_port_details(mcp_mocks):
    ds = DatasetFactory()
    with mcp_mocks():
        result = get_output_port_details(output_port_id=str(ds.id))
    assert result["id"] == ds.id


def test_get_technical_asset_details(mcp_mocks):
    ta = TechnicalAssetFactory()
    with mcp_mocks():
        result = get_technical_asset_details(technical_asset_id=str(ta.id))
    assert result["id"] == ta.id


def test_get_domain_details(mcp_mocks):
    domain = DomainFactory()
    with mcp_mocks():
        result = get_domain_details(domain_id=str(domain.id))
    assert result["id"] == domain.id


def test_search_data_products(mcp_mocks):
    dp1 = DataProductFactory(name="Alpha Product", description="alpha description")
    dp2 = DataProductFactory(name="Beta Product", description="beta description")

    with mcp_mocks():
        result = search_data_products(query="Alpha")

    assert "data_products" in result
    assert result["count"] == 1
    returned_names = {dp["name"] for dp in result["data_products"]}
    assert dp1.name in returned_names
    assert dp2.name not in returned_names


def test_search_data_products_no_query(mcp_mocks):
    DataProductFactory()
    DataProductFactory()

    with mcp_mocks():
        result = search_data_products(query=None)

    assert "data_products" in result
    assert result["count"] >= 2


def test_search_data_products_by_domain(mcp_mocks):
    domain = DomainFactory()
    dp_in_domain = DataProductFactory(domain=domain)
    DataProductFactory()  # different domain

    with mcp_mocks():
        result = search_data_products(domain_id=str(domain.id))

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert dp_in_domain.id in returned_ids
    assert result["count"] == 1


def test_search_data_products_by_status(mcp_mocks):
    from app.data_products.status import DataProductStatus

    active_dp = DataProductFactory(status=DataProductStatus.ACTIVE.value)
    DataProductFactory(status=DataProductStatus.PENDING.value)

    with mcp_mocks():
        result = search_data_products(status=DataProductStatus.ACTIVE.value)

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert active_dp.id in returned_ids
    for dp in result["data_products"]:
        assert dp["status"] == "active"


def test_search_data_products_limit(mcp_mocks):
    for _ in range(5):
        DataProductFactory()

    with mcp_mocks():
        result = search_data_products(query=None, limit=2)

    assert result["count"] <= 2
    assert len(result["data_products"]) <= 2


def test_search_data_products_filters_applied(mcp_mocks):
    with mcp_mocks():
        result = search_data_products(query="test", domain_id=None, status="active")

    assert result["filters_applied"]["query"] == "test"
    assert result["filters_applied"]["domain_id"] is None
    assert result["filters_applied"]["status"] == "active"


def test_search_data_products_matches_description(mcp_mocks):
    dp = DataProductFactory(name="IrrelevantName", description="unique_needle_xyz")
    DataProductFactory(name="OtherProduct", description="something else")

    with mcp_mocks():
        result = search_data_products(query="unique_needle_xyz")

    assert result["count"] == 1
    assert result["data_products"][0]["id"] == dp.id
