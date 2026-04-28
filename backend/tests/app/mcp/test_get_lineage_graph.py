# ruff: noqa: S106
import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.mcp.mcp import get_lineage_graph  # type: ignore[attr-defined]

PRODUCT_ID = str(uuid4())
PORT_ID = str(uuid4())
CONSUMER_ID = str(uuid4())


def _make_node(node_id, node_type, name):
    node = MagicMock()
    node.model_dump.return_value = {
        "id": node_id,
        "type": node_type,
        "data": {"name": name},
    }
    return node


def _make_edge(edge_id, source, target, animated):
    edge = MagicMock()
    edge.model_dump.return_value = {
        "id": edge_id,
        "source": source,
        "target": target,
        "animated": animated,
    }
    return edge


@patch("app.mcp.mcp.get_db_session")
@patch("app.mcp.mcp.GraphService")
class TestGetLineageGraph:
    def test_returns_nodes_and_edges(self, mock_graph_svc_cls, mock_get_db):
        mock_get_db.return_value = iter([MagicMock()])
        product_node = _make_node(
            PRODUCT_ID, "dataProductNode", "Marketing Customer 360"
        )
        port_node = _make_node(PORT_ID, "datasetNode", "Customer Segments")
        consumer_node = _make_node(CONSUMER_ID, "dataProductNode", "Sales Analytics")
        ownership_edge = _make_edge(
            f"{PRODUCT_ID}-{PORT_ID}", PRODUCT_ID, PORT_ID, True
        )
        access_edge = _make_edge(f"{PORT_ID}-{CONSUMER_ID}", PORT_ID, CONSUMER_ID, True)

        mock_graph = MagicMock()
        mock_graph.nodes = [product_node, port_node, consumer_node]
        mock_graph.edges = [ownership_edge, access_edge]
        mock_graph_svc_cls.return_value.get_graph_data.return_value = mock_graph

        result = get_lineage_graph()

        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 3
        assert len(result["edges"]) == 2
        json.dumps(result)  # must not raise

    def test_calls_graph_service_with_both_node_types(
        self, mock_graph_svc_cls, mock_get_db
    ):
        mock_get_db.return_value = iter([MagicMock()])
        mock_graph = MagicMock()
        mock_graph.nodes = []
        mock_graph.edges = []
        mock_graph_svc_cls.return_value.get_graph_data.return_value = mock_graph

        get_lineage_graph()

        mock_graph_svc_cls.return_value.get_graph_data.assert_called_once_with(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

    def test_animated_true_for_approved_edges(self, mock_graph_svc_cls, mock_get_db):
        mock_get_db.return_value = iter([MagicMock()])
        approved_edge = _make_edge(
            f"{PORT_ID}-{CONSUMER_ID}", PORT_ID, CONSUMER_ID, True
        )
        pending_edge = _make_edge(f"{PORT_ID}-other", PORT_ID, "other", False)

        mock_graph = MagicMock()
        mock_graph.nodes = []
        mock_graph.edges = [approved_edge, pending_edge]
        mock_graph_svc_cls.return_value.get_graph_data.return_value = mock_graph

        result = get_lineage_graph()

        animated = [e for e in result["edges"] if e["animated"]]
        not_animated = [e for e in result["edges"] if not e["animated"]]
        assert len(animated) == 1
        assert len(not_animated) == 1

    def test_returns_error_on_exception(self, mock_graph_svc_cls, mock_get_db):
        mock_get_db.return_value = iter([MagicMock()])
        mock_graph_svc_cls.return_value.get_graph_data.side_effect = RuntimeError(
            "db down"
        )

        result = get_lineage_graph()

        assert "error" in result
        assert "db down" in result["error"]

    def test_closes_db_session(self, mock_graph_svc_cls, mock_get_db):
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_graph = MagicMock()
        mock_graph.nodes = []
        mock_graph.edges = []
        mock_graph_svc_cls.return_value.get_graph_data.return_value = mock_graph

        get_lineage_graph()

        mock_db.close.assert_called_once()
