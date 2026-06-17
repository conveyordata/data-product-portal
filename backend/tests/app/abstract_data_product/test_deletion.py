import pytest
from fastapi import HTTPException

from app.abstract_data_product.service import AbstractDataProductService
from app.data_products.status import DataProductStatus
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    ExplorationFactory,
    UserFactory,
)


class TestMarkForDeletion:
    def test_returns_true_when_no_finalizers(self, session):
        """Deletion proceeds immediately when there are no finalizers."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=[])

        can_delete = service.mark_for_deletion(dp.id)

        assert can_delete is True
        # Status should not change — caller is responsible for actual deletion
        assert dp.status != DataProductStatus.DELETING

    def test_returns_false_and_marks_deleting_when_finalizers_present(self, session):
        """Deletion is blocked and status becomes DELETING when finalizers exist."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=["some-system"])

        can_delete = service.mark_for_deletion(dp.id)

        assert can_delete is False
        session.refresh(dp)
        assert dp.status == DataProductStatus.DELETING

    def test_works_for_explorations_too(self, session):
        """Finalizer logic applies to explorations via abstract base."""
        service = AbstractDataProductService(db=session)
        exploration = ExplorationFactory(finalizers=["cleanup-job"])

        can_delete = service.mark_for_deletion(exploration.id)

        assert can_delete is False
        session.refresh(exploration)
        assert exploration.status == DataProductStatus.DELETING

    def test_raises_for_unknown_id(self, session):
        import uuid

        service = AbstractDataProductService(db=session)

        with pytest.raises(HTTPException) as exc_info:
            service.mark_for_deletion(uuid.uuid4())

        assert exc_info.value.status_code == 404


class TestAddFinalizer:
    def test_adds_finalizer(self, session):
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=[])

        service.add_finalizer(dp.id, "my-system")

        session.refresh(dp)
        assert "my-system" in dp.finalizers

    def test_multiple_finalizers_accumulate(self, session):
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=[])

        service.add_finalizer(dp.id, "system-a")
        service.add_finalizer(dp.id, "system-b")

        session.refresh(dp)
        assert "system-a" in dp.finalizers
        assert "system-b" in dp.finalizers
        assert len(dp.finalizers) == 2

    def test_duplicate_finalizer_raises_409(self, session):
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=["existing"])

        with pytest.raises(HTTPException) as exc_info:
            service.add_finalizer(dp.id, "existing")

        assert exc_info.value.status_code == 409
        assert "existing" in exc_info.value.detail


class TestRemoveFinalizer:
    def test_remove_finalizer_not_deleting_returns_false(self, session):
        """Removing a finalizer from a non-DELETING product never triggers deletion."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=["my-system"])

        should_delete = service.remove_finalizer(dp.id, "my-system")

        assert should_delete is False
        session.refresh(dp)
        assert dp.finalizers == []

    def test_remove_last_finalizer_while_deleting_returns_true(self, session):
        """Removing the last finalizer from a DELETING product signals the caller to delete."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(
            finalizers=["last-one"], status=DataProductStatus.DELETING.value
        )

        should_delete = service.remove_finalizer(dp.id, "last-one")

        assert should_delete is True
        session.refresh(dp)
        assert dp.finalizers == []

    def test_remove_one_of_many_finalizers_while_deleting_returns_false(self, session):
        """Still has remaining finalizers — do not delete yet."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(
            finalizers=["a", "b"], status=DataProductStatus.DELETING.value
        )

        should_delete = service.remove_finalizer(dp.id, "a")

        assert should_delete is False
        session.refresh(dp)
        assert dp.finalizers == ["b"]

    def test_remove_nonexistent_finalizer_raises_404(self, session):
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=["something-else"])

        with pytest.raises(HTTPException) as exc_info:
            service.remove_finalizer(dp.id, "does-not-exist")

        assert exc_info.value.status_code == 404
        assert "does-not-exist" in exc_info.value.detail


class TestFullDeletionLifecycle:
    def test_add_finalizer_then_delete_then_remove_finalizer(self, session):
        """
        Full lifecycle:
        1. Add a finalizer before deletion is requested.
        2. Request deletion — blocked, product enters DELETING.
        3. Remove the finalizer — returns True (caller should now delete).
        """
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=[])

        service.add_finalizer(dp.id, "my-cleanup-job")
        can_delete = service.mark_for_deletion(dp.id)

        assert can_delete is False
        session.refresh(dp)
        assert dp.status == DataProductStatus.DELETING
        assert "my-cleanup-job" in dp.finalizers

        should_delete = service.remove_finalizer(dp.id, "my-cleanup-job")

        assert should_delete is True

    def test_delete_with_no_finalizers_skips_deleting_state(self, session):
        """When there are no finalizers, mark_for_deletion returns True immediately."""
        service = AbstractDataProductService(db=session)
        dp = DataProductFactory(finalizers=[])

        can_delete = service.mark_for_deletion(dp.id)

        assert can_delete is True
        session.refresh(dp)
        assert dp.status != DataProductStatus.DELETING


class TestEnsureNotDeleting:
    def test_request_input_ports_blocked_for_deleting_consumer(self, session):
        """A data product in DELETING state cannot consume new output ports."""
        service = AbstractDataProductService(db=session)
        actor = UserFactory()
        consumer = DataProductFactory(status=DataProductStatus.DELETING.value)
        output_port = DatasetFactory()

        with pytest.raises(HTTPException) as exc_info:
            service.request_input_ports(
                id=consumer.id,
                output_port_ids=[output_port.id],
                justification="test",
                actor=actor,
            )

        assert exc_info.value.status_code == 409
        assert consumer.name in exc_info.value.detail

    def test_request_input_ports_blocked_when_provider_is_deleting(self, session):
        """Cannot consume an output port whose owning data product is DELETING."""
        service = AbstractDataProductService(db=session)
        actor = UserFactory()
        consumer = DataProductFactory(status=DataProductStatus.ACTIVE.value)
        provider = DataProductFactory(status=DataProductStatus.DELETING.value)
        output_port = DatasetFactory(data_product=provider)

        with pytest.raises(HTTPException) as exc_info:
            service.request_input_ports(
                id=consumer.id,
                output_port_ids=[output_port.id],
                justification="test",
                actor=actor,
            )

        assert exc_info.value.status_code == 409
        assert provider.name in exc_info.value.detail
