import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.configuration.domains.model import Domain as DomainModel
from app.configuration.domains.service import DomainService
from app.configuration.domains.status import DomainStatus
from tests import engine
from tests.factories import DataProductFactory, DomainFactory, ExplorationFactory


def _remove_unknown_finalizer(service, id):
    with pytest.raises(HTTPException):
        service.remove_finalizer(id, "unknown")


@pytest.mark.parametrize(
    ("finalizers", "call"),
    [
        ([], lambda service, id: service.ensure_assignable(id)),
        ([], lambda service, id: service.mark_for_deletion(id)),
        (["existing"], lambda service, id: service.add_finalizer(id, "existing")),
        (["existing"], _remove_unknown_finalizer),
    ],
    ids=["ensure_assignable", "mark_for_deletion", "add_finalizer", "remove_finalizer"],
)
def test_domain_checks__lock_the_domain_until_commit(session, finalizers, call):
    domain = DomainFactory(finalizers=finalizers)
    call(DomainService(session), domain.id)
    try:
        with engine.connect() as other, pytest.raises(OperationalError):
            other.execute(
                select(DomainModel.id)
                .where(DomainModel.id == domain.id)
                .with_for_update(nowait=True)
            )
    finally:
        session.rollback()


def test_database__rejects_data_product_in_deleting_domain(session):
    domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["x"])
    with pytest.raises(IntegrityError, match="pending deletion"):
        DataProductFactory(domain=domain)
    session.rollback()


def test_database__rejects_moving_exploration_into_deleting_domain(session):
    exploration = ExplorationFactory()
    deleting = DomainFactory(status=DomainStatus.DELETING, finalizers=["x"])
    exploration.domain_id = deleting.id
    with pytest.raises(IntegrityError, match="pending deletion"):
        session.flush()
    session.rollback()


def test_database__allows_other_updates_in_deleting_domain(session):
    domain = DomainFactory(finalizers=["x"])
    data_product = DataProductFactory(domain=domain)
    domain.status = DomainStatus.DELETING
    session.flush()
    try:
        data_product.name = "renamed"
        session.flush()
    finally:
        session.rollback()


def test_remove_finalizer__last_one_with_data_product_cancels_deletion(session):
    domain = DomainFactory(finalizers=["provisioner"])
    DataProductFactory(domain=domain)
    domain.status = DomainStatus.DELETING
    session.flush()
    try:
        should_delete = DomainService(session).remove_finalizer(
            domain.id, "provisioner"
        )

        assert should_delete is False
        assert domain.status == DomainStatus.ACTIVE
        assert domain.finalizers == []
    finally:
        session.rollback()
