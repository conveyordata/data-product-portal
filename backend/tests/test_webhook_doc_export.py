# backend/tests/test_webhook_doc_export.py

import pytest

from app.main import app
from app.webhook_doc_export import build_event_list, generate_markdown, render_payload


@pytest.fixture(scope="module")
def events():
    return build_event_list(app)


def test_build_event_list_finds_all_events(events):
    assert len(events) > 0


def test_build_event_list_no_duplicates(events):
    keys = [(e["event"], e["method"], e["path"]) for e in events]
    assert len(keys) == len(set(keys))


def test_build_event_list_sorted_by_event_name(events):
    names = [e["event"] for e in events]
    assert names == sorted(names)


def test_known_data_product_event_present(events):
    event_types = {e["event"] for e in events}
    assert "data_product.created" in event_types
    assert "data_product.deleted" in event_types
    assert "data_product.team_member_added" in event_types


def test_known_output_port_event_present(events):
    event_types = {e["event"] for e in events}
    assert "output_port.created" in event_types
    assert "output_port.link_approved" in event_types


def test_known_technical_asset_event_present(events):
    event_types = {e["event"] for e in events}
    assert "technical_asset.created" in event_types
    assert "technical_asset.linked" in event_types


def test_data_product_created_event_shape(events):
    created = next(e for e in events if e["event"] == "data_product.created")
    assert created["method"] == "POST"
    assert "data_product" in created["payload"]
    assert created["payload"]["data_product"] == "GetDataProductResponse"


def test_output_port_created_event_shape(events):
    created = next(e for e in events if e["event"] == "output_port.created")
    assert "data_product" in created["payload"]
    assert "output_port" in created["payload"]
    assert created["payload"]["output_port"] == "GetOutputPortResponse"


def test_technical_asset_created_event_shape(events):
    created = next(e for e in events if e["event"] == "technical_asset.created")
    assert "technical_asset" in created["payload"]
    assert created["payload"]["technical_asset"] == "GetTechnicalAssetsResponseItem"


def test_generate_markdown_contains_all_groups(events):
    md = generate_markdown(events)
    assert "### Data Product Events" in md
    assert "### Output Port Events" in md
    assert "### Technical Asset Events" in md


def test_generate_markdown_contains_event_rows(events):
    md = generate_markdown(events)
    assert "`data_product.created`" in md
    assert "`output_port.created`" in md
    assert "`technical_asset.created`" in md


def test_render_payload_empty():
    assert render_payload({}) == "—"


def test_render_payload_single_field():
    result = render_payload({"data_product": "GetDataProductResponse"})
    assert "`data_product`" in result
    assert "GetDataProductResponse" in result
