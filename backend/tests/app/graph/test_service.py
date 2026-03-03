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
        consumer_pending = DataProductFactory()
        consumer_denied = DataProductFactory()

        # Create links with different statuses
        DataProductDatasetAssociationFactory(
            data_product=consumer_approved,
            dataset=dataset,
            status=DecisionStatus.APPROVED,
        )
        DataProductDatasetAssociationFactory(
            data_product=consumer_pending,
            dataset=dataset,
            status=DecisionStatus.PENDING,
        )
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

        # Find edges from dataset to consumers
        edges = list(graph_data.edges)
        consumer_edges = [
            edge
            for edge in edges
            if str(edge.source) == str(dataset.id)
            and str(edge.target)
            in [
                str(consumer_approved.id),
                str(consumer_pending.id),
                str(consumer_denied.id),
            ]
        ]

        # Check that only the approved link is animated
        animated_edges = [edge for edge in consumer_edges if edge.animated]
        non_animated_edges = [edge for edge in consumer_edges if not edge.animated]

        assert len(animated_edges) == 1, (
            f"Expected exactly 1 animated edge (approved), got {len(animated_edges)}"
        )
        assert len(non_animated_edges) == 2, (
            f"Expected exactly 2 non-animated edges (pending + denied), got {len(non_animated_edges)}"
        )

        # Verify the animated edge is the approved one
        approved_edge = animated_edges[0]
        assert str(approved_edge.target) == str(consumer_approved.id), (
            "The animated edge should point to the approved consumer"
        )

    def test_graph_data_products_only_view_respects_status(self):
        """
        Test that data products-only view correctly animates only approved links.
        """
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer_approved = DataProductFactory()
        consumer_pending = DataProductFactory()

        DataProductDatasetAssociationFactory(
            data_product=consumer_approved,
            dataset=dataset,
            status=DecisionStatus.APPROVED,
        )
        DataProductDatasetAssociationFactory(
            data_product=consumer_pending,
            dataset=dataset,
            status=DecisionStatus.PENDING,
        )

        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=False,
        )

        edges = list(graph_data.edges)

        # Only the approved edge should be animated
        animated_edges = [edge for edge in edges if edge.animated]
        assert len(animated_edges) == 1, (
            f"Expected 1 animated edge, got {len(animated_edges)}"
        )

        # The animated edge should be to the approved consumer
        approved_edge = animated_edges[0]
        assert str(approved_edge.target) == str(consumer_approved.id)
        assert str(approved_edge.source) == str(producer.id)

    def test_graph_datasets_only_view_respects_status(self):
        """
        Test that datasets-only view correctly animates only approved links.
        """
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)
        consumer_approved = DataProductFactory()
        DatasetFactory(data_product=consumer_approved)
        consumer_pending = DataProductFactory()

        DataProductDatasetAssociationFactory(
            data_product=consumer_approved,
            dataset=dataset,
            status=DecisionStatus.APPROVED,
        )
        DataProductDatasetAssociationFactory(
            data_product=consumer_pending,
            dataset=dataset,
            status=DecisionStatus.PENDING,
        )

        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=False,
            dataset_nodes_enabled=True,
        )
        edges = list(graph_data.edges)

        # Count animated vs non-animated edges
        animated_count = sum(1 for edge in edges if edge.animated)

        # At least one edge should be animated (the approved dataset consumption)
        assert animated_count >= 1, (
            f"Expected at least 1 animated edge for approved status, got {animated_count}"
        )

    def test_all_statuses_create_edges_but_only_approved_animates(self):
        """
        Test that all statuses create edges, but only APPROVED edges are animated.
        This is the core behavior that the enum fix ensures.
        """
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)

        # Create one consumer for each status
        consumers = {}
        for status in DecisionStatus:
            consumer = DataProductFactory()
            DataProductDatasetAssociationFactory(
                data_product=consumer,
                dataset=dataset,
                status=status,
            )
            consumers[status] = consumer

        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

        edges = list(graph_data.edges)

        # Find edges from dataset to our test consumers
        test_consumer_ids = {str(c.id) for c in consumers.values()}
        consumer_edges = [
            edge
            for edge in edges
            if str(edge.source) == str(dataset.id)
            and str(edge.target) in test_consumer_ids
        ]

        # Should have one edge per status
        assert len(consumer_edges) == len(DecisionStatus), (
            f"Expected {len(DecisionStatus)} edges, got {len(consumer_edges)}"
        )

        # Check animation status
        for edge in consumer_edges:
            target_id = str(edge.target)
            # Find which status this edge corresponds to
            status_for_edge = None
            for status, consumer in consumers.items():
                if str(consumer.id) == target_id:
                    status_for_edge = status
                    break

            # Only APPROVED should be animated
            if status_for_edge == DecisionStatus.APPROVED:
                assert edge.animated, "Edge to APPROVED consumer should be animated"
            else:
                assert not edge.animated, (
                    f"Edge to {status_for_edge} consumer should NOT be animated"
                )

    def test_multiple_approved_links_all_animate(self):
        """
        Test that when multiple links are approved, they all animate.
        """
        producer = DataProductFactory()
        dataset = DatasetFactory(data_product=producer)

        # Create multiple approved consumers
        approved_consumers = [DataProductFactory() for _ in range(3)]

        for consumer in approved_consumers:
            DataProductDatasetAssociationFactory(
                data_product=consumer,
                dataset=dataset,
                status=DecisionStatus.APPROVED,
            )

        service = GraphService(test_session)
        graph_data = service.get_graph_data(
            data_product_nodes_enabled=True,
            dataset_nodes_enabled=True,
        )

        edges = list(graph_data.edges)

        # Find edges to our approved consumers
        approved_consumer_ids = {str(c.id) for c in approved_consumers}
        approved_edges = [
            edge
            for edge in edges
            if str(edge.source) == str(dataset.id)
            and str(edge.target) in approved_consumer_ids
        ]

        # All should be animated
        assert len(approved_edges) == 3
        for edge in approved_edges:
            assert edge.animated, "All edges to approved consumers should be animated"
