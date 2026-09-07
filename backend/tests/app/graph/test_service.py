"""
Tests for graph service to ensure enum values are correctly compared with SQL query results.

The bug: PostgreSQL returns enum values as uppercase strings (e.g., 'APPROVED'),
but DecisionStatus enum values are lowercase (e.g., 'approved').
The fix: Use DecisionStatus.APPROVED.name (uppercase) instead of the enum object directly.
"""

from app.authorization.role_assignments.enums import DecisionStatus
from app.graph.service import GraphService
from tests.factories import (
    DataProductFactory,
    InputPortFactory,
    OutputPortFactory,
    UserFactory,
)
from tests.session_util import as_user


class TestGraphServiceEnumMatching:
    """Tests to ensure enum comparisons work correctly with PostgreSQL enum values."""

    def test_graph_service_correctly_identifies_approved_links(self, session):
        """
        Test that the graph service correctly identifies approved links as animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = OutputPortFactory(data_product=producer)
        consumer_approved = DataProductFactory()

        # Create links with different statuses
        InputPortFactory(
            consuming_abstract_data_product=consumer_approved,
            output_port=dataset,
            status=DecisionStatus.APPROVED,
        )

        with as_user(session, UserFactory().id):
            graph_data = GraphService(session).get_graph_data(
                output_port_nodes_enabled=True,
            )

        assert len(graph_data.edges) == 2

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 2

    def test_graph_service_correctly_identifies_pending_links(self, session):
        """
        Test that the graph service correctly identifies pending links as not animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = OutputPortFactory(data_product=producer)
        consumer_pending = DataProductFactory()

        # Create links with different statuses
        InputPortFactory(
            consuming_abstract_data_product=consumer_pending,
            output_port=dataset,
            status=DecisionStatus.PENDING,
        )

        with as_user(session, UserFactory().id):
            graph_data = GraphService(session).get_graph_data(
                output_port_nodes_enabled=True,
            )

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 1

    def test_graph_service_correctly_identifies_denied_links(self, session):
        """
        Test that the graph service correctly identifies denied links as not animated.
        This verifies the fix for comparing SQL enum strings with Python enum values.
        """
        # Create data products with different statuses
        producer = DataProductFactory()
        dataset = OutputPortFactory(data_product=producer)
        consumer_denied = DataProductFactory()

        # Create links with different statuses
        InputPortFactory(
            consuming_abstract_data_product=consumer_denied,
            output_port=dataset,
            status=DecisionStatus.DENIED,
        )

        with as_user(session, UserFactory().id):
            graph_data = GraphService(session).get_graph_data(
                output_port_nodes_enabled=True,
            )

        # Check that only the approved link is animated
        animated_edges = [edge for edge in graph_data.edges if edge.animated]

        assert len(animated_edges) == 1
