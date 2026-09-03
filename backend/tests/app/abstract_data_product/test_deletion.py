import pytest
from fastapi import HTTPException

from app.abstract_data_product.schema_request import (
    RequestInputPortsForAbstractDataProductRequestItem,
)
from app.data_products.status import AbstractDataProductStatus
from tests.factories import (
    DataProductFactory,
    ExplorationFactory,
    OutputPortFactory,
    UserFactory,
)


class TestMarkForDeletion:
    def test_returns_true_when_no_finalizers(
        self, session, abstract_data_product_service
    ):
        """Deletion proceeds immediately when there are no finalizers."""
        dp = DataProductFactory(finalizers=[])

        can_delete = abstract_data_product_service.mark_for_deletion(dp.id)

        assert can_delete is True
        # Status should not change — caller is responsible for actual deletion
        assert dp.status != AbstractDataProductStatus.DELETING

    def test_returns_false_and_marks_deleting_when_finalizers_present(
        self, session, abstract_data_product_service
    ):
        """Deletion is blocked and status becomes DELETING when finalizers exist."""
        dp = DataProductFactory(finalizers=["some-system"])

        can_delete = abstract_data_product_service.mark_for_deletion(dp.id)

        assert can_delete is False
        session.refresh(dp)
        assert dp.status == AbstractDataProductStatus.DELETING

    def test_works_for_explorations_too(self, session, abstract_data_product_service):
        """Finalizer logic applies to explorations via abstract base."""
        exploration = ExplorationFactory(finalizers=["cleanup-job"])

        can_delete = abstract_data_product_service.mark_for_deletion(exploration.id)

        assert can_delete is False
        session.refresh(exploration)
        assert exploration.status == AbstractDataProductStatus.DELETING

    def test_raises_for_unknown_id(self, abstract_data_product_service):
        import uuid

        with pytest.raises(HTTPException) as exc_info:
            abstract_data_product_service.mark_for_deletion(uuid.uuid4())

        assert exc_info.value.status_code == 404


class TestAddFinalizer:
    def test_adds_finalizer(self, session, abstract_data_product_service):
        dp = DataProductFactory(finalizers=[])

        abstract_data_product_service.add_finalizer(dp.id, "my-system")

        session.refresh(dp)
        assert "my-system" in dp.finalizers

    def test_multiple_finalizers_accumulate(
        self, session, abstract_data_product_service
    ):
        dp = DataProductFactory(finalizers=[])

        abstract_data_product_service.add_finalizer(dp.id, "system-a")
        abstract_data_product_service.add_finalizer(dp.id, "system-b")

        session.refresh(dp)
        assert "system-a" in dp.finalizers
        assert "system-b" in dp.finalizers
        assert len(dp.finalizers) == 2

    def test_duplicate_finalizer_is_idempotent(
        self, session, abstract_data_product_service
    ):
        dp = DataProductFactory(finalizers=["existing"])

        result = abstract_data_product_service.add_finalizer(dp.id, "existing")

        session.refresh(dp)
        assert dp.finalizers == ["existing"]
        assert result.id == dp.id

    def test_add_finalizer_blocked_when_already_deleting(
        self, session, abstract_data_product_service
    ):
        dp = DataProductFactory(
            finalizers=[], status=AbstractDataProductStatus.DELETING.value
        )

        with pytest.raises(HTTPException) as exc_info:
            abstract_data_product_service.add_finalizer(dp.id, "new-system")

        assert exc_info.value.status_code == 409


class TestRemoveFinalizer:
    def test_remove_finalizer_not_deleting_returns_false(
        self, session, abstract_data_product_service
    ):
        """Removing a finalizer from a non-DELETING product never triggers deletion."""
        dp = DataProductFactory(finalizers=["my-system"])

        should_delete = abstract_data_product_service.remove_finalizer(
            dp.id, "my-system"
        )

        assert should_delete is False
        session.refresh(dp)
        assert dp.finalizers == []

    def test_remove_last_finalizer_while_deleting_returns_true(
        self, session, abstract_data_product_service
    ):
        """Removing the last finalizer from a DELETING product signals the caller to delete."""
        dp = DataProductFactory(
            finalizers=["last-one"], status=AbstractDataProductStatus.DELETING.value
        )

        should_delete = abstract_data_product_service.remove_finalizer(
            dp.id, "last-one"
        )

        assert should_delete is True
        session.refresh(dp)
        assert dp.finalizers == []

    def test_remove_one_of_many_finalizers_while_deleting_returns_false(
        self, session, abstract_data_product_service
    ):
        """Still has remaining finalizers — do not delete yet."""
        dp = DataProductFactory(
            finalizers=["a", "b"], status=AbstractDataProductStatus.DELETING.value
        )

        should_delete = abstract_data_product_service.remove_finalizer(dp.id, "a")

        assert should_delete is False
        session.refresh(dp)
        assert dp.finalizers == ["b"]

    def test_remove_nonexistent_finalizer_raises_404(
        self, session, abstract_data_product_service
    ):
        dp = DataProductFactory(finalizers=["something-else"])

        with pytest.raises(HTTPException) as exc_info:
            abstract_data_product_service.remove_finalizer(dp.id, "does-not-exist")

        assert exc_info.value.status_code == 404
        assert "does-not-exist" in exc_info.value.detail


class TestFullDeletionLifecycle:
    def test_add_finalizer_then_delete_then_remove_finalizer(
        self, session, abstract_data_product_service
    ):
        """
        Full lifecycle:
        1. Add a finalizer before deletion is requested.
        2. Request deletion — blocked, product enters DELETING.
        3. Remove the finalizer — returns True (caller should now delete).
        """
        dp = DataProductFactory(finalizers=[])

        abstract_data_product_service.add_finalizer(dp.id, "my-cleanup-job")
        can_delete = abstract_data_product_service.mark_for_deletion(dp.id)

        assert can_delete is False
        session.refresh(dp)
        assert dp.status == AbstractDataProductStatus.DELETING
        assert "my-cleanup-job" in dp.finalizers

        should_delete = abstract_data_product_service.remove_finalizer(
            dp.id, "my-cleanup-job"
        )

        assert should_delete is True

    def test_delete_with_no_finalizers_skips_deleting_state(
        self, session, abstract_data_product_service
    ):
        """When there are no finalizers, mark_for_deletion returns True immediately."""
        dp = DataProductFactory(finalizers=[])

        can_delete = abstract_data_product_service.mark_for_deletion(dp.id)

        assert can_delete is True
        session.refresh(dp)
        assert dp.status != AbstractDataProductStatus.DELETING


class TestEnsureNotDeleting:
    def test_request_input_ports_blocked_for_deleting_consumer(
        self, session, abstract_data_product_service
    ):
        """A data product in DELETING state cannot consume new output ports."""
        actor = UserFactory()
        consumer = DataProductFactory(status=AbstractDataProductStatus.DELETING.value)
        output_port = OutputPortFactory()

        with pytest.raises(HTTPException) as exc_info:
            abstract_data_product_service.request_input_ports(
                id=consumer.id,
                output_ports_requested=[
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=output_port.id
                    )
                ],
                justification="test",
                actor=actor,
            )

        assert exc_info.value.status_code == 409
        assert consumer.name in exc_info.value.detail

    def test_request_input_ports_blocked_when_provider_is_deleting(
        self, session, abstract_data_product_service
    ):
        """Cannot consume an output port whose owning data product is DELETING."""
        actor = UserFactory()
        consumer = DataProductFactory(status=AbstractDataProductStatus.ACTIVE.value)
        provider = DataProductFactory(status=AbstractDataProductStatus.DELETING.value)
        output_port = OutputPortFactory(data_product=provider)

        with pytest.raises(HTTPException) as exc_info:
            abstract_data_product_service.request_input_ports(
                id=consumer.id,
                output_ports_requested=[
                    RequestInputPortsForAbstractDataProductRequestItem(
                        output_port_id=output_port.id
                    )
                ],
                justification="test",
                actor=actor,
            )

        assert exc_info.value.status_code == 409
        assert provider.name in exc_info.value.detail
