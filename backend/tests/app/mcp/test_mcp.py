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


def test_search_output_ports(session):
    ds1 = DatasetFactory(name="Customer Data")
    ds2 = DatasetFactory(name="Sales Data")
    OutputPortService(db=session).recalculate_search_for_all_output_ports()

    result = search_output_ports(query="Data", db=session)

    assert "output_ports" in result
    assert result["count"] >= 2
    returned_names = {op["name"] for op in result["output_ports"]}
    assert ds1.name in returned_names
    assert ds2.name in returned_names


def test_search_output_ports_no_query(session):
    DatasetFactory(name="Customer Data")
    OutputPortService(db=session).recalculate_search_for_all_output_ports()

    result = search_output_ports(query=None, db=session)

    assert "output_ports" in result
    assert result["count"] == 1


def test_get_data_product_details(session):
    dp = DataProductFactory()
    result = get_data_product_details(data_product_id=str(dp.id), db=session)
    assert result["id"] == dp.id


def test_get_output_port_details(session):
    ds = DatasetFactory()
    result = get_output_port_details(output_port_id=str(ds.id), db=session)
    assert result["id"] == ds.id


def test_get_technical_asset_details(session):
    ta = TechnicalAssetFactory()
    result = get_technical_asset_details(technical_asset_id=str(ta.id), db=session)
    assert result["id"] == ta.id


def test_get_domain_details(session):
    domain = DomainFactory()
    result = get_domain_details(domain_id=str(domain.id), db=session)
    assert result["id"] == domain.id


def test_search_data_products(session):
    dp1 = DataProductFactory(name="Alpha Product", description="alpha description")
    dp2 = DataProductFactory(name="Beta Product", description="beta description")

    result = search_data_products(query="Alpha", db=session)

    assert "data_products" in result
    assert result["count"] == 1
    returned_names = {dp["name"] for dp in result["data_products"]}
    assert dp1.name in returned_names
    assert dp2.name not in returned_names


def test_search_data_products_no_query(session):
    DataProductFactory()
    DataProductFactory()

    result = search_data_products(query=None, db=session)

    assert "data_products" in result
    assert result["count"] >= 2


def test_search_data_products_by_domain(session):
    domain = DomainFactory()
    dp_in_domain = DataProductFactory(domain=domain)
    DataProductFactory()  # different domain

    result = search_data_products(domain_id=str(domain.id), db=session)

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert dp_in_domain.id in returned_ids
    assert result["count"] == 1


def test_search_data_products_by_status(session):
    from app.data_products.status import DataProductStatus

    active_dp = DataProductFactory(status=DataProductStatus.ACTIVE.value)
    DataProductFactory(status=DataProductStatus.PENDING.value)

    result = search_data_products(status=DataProductStatus.ACTIVE.value, db=session)

    assert "data_products" in result
    returned_ids = {dp["id"] for dp in result["data_products"]}
    assert active_dp.id in returned_ids
    for dp in result["data_products"]:
        assert dp["status"] == "active"


def test_search_data_products_limit(session):
    for _ in range(5):
        DataProductFactory()

    result = search_data_products(query=None, limit=2, db=session)

    assert result["count"] <= 2
    assert len(result["data_products"]) <= 2


def test_search_data_products_filters_applied(session):
    result = search_data_products(
        query="test", domain_id=None, status="active", db=session
    )

    assert result["filters_applied"]["query"] == "test"
    assert result["filters_applied"]["domain_id"] is None
    assert result["filters_applied"]["status"] == "active"


def test_search_data_products_matches_description(session):
    dp = DataProductFactory(name="IrrelevantName", description="unique_needle_xyz")
    DataProductFactory(name="OtherProduct", description="something else")

    result = search_data_products(query="unique_needle_xyz", db=session)

    assert result["count"] == 1
    assert result["data_products"][0]["id"] == dp.id
