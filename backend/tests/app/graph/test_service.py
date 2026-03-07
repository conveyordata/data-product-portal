"""
Tests for graph service to ensure enum values are correctly compared with SQL query results.

The bug: PostgreSQL returns enum values as uppercase strings (e.g., 'APPROVED'),
but DecisionStatus enum values are lowercase (e.g., 'approved').
The fix: Use DecisionStatus.APPROVED.name (uppercase) instead of the enum object directly.
"""

from app.authorization.role_assignments.enums import DecisionStatus
from app.graph.service import GraphService
from tests import test_session
from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DatasetFactory,
)


class TestGraphServiceEnumMatching:
    """Tests to ensure enum comparisons work correctly with PostgreSQL enum values."""

    def test_graph_service_correctly_identifies_approved_links(self):
        """
        Test that the graph service correctly identifies approved links as animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer_approved = DataProductFactory()

        # Create links with different statuses
        DataProductDatasetAssociationFactory(
            data_product=consumer_approved,
            dataset=dataset,
            status=DecisionStatus.APPROVED,
        )

        # Get graph data
        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 2

    def test_graph_service_correctly_identifies_pending_links(self):
        """
        Test that the graph service correctly identifies pending links as not animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer_pending = DataProductFactory()

        # Create links with different statuses
        DataProductDatasetAssociationFactory(
            data_product=consumer_pending,
            dataset=dataset,
            status=DecisionStatus.PENDING,
        )

        # Get graph data
        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 1

    def test_graph_service_correctly_identifies_denied_links(self):
        """
        Test that the graph service correctly identifies denied links as not animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer_denied = DataProductFactory()

        # Create links with different statuses
        DataProductDatasetAssociationFactory(
            data_product=consumer_denied,
            dataset=dataset,
            status=DecisionStatus.DENIED,
        )

        # Get graph data
        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 1
