import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.configuration.domains.model import Domain as DomainModel
from app.configuration.domains.model import domain_environment_table
from app.configuration.domains.schema_request import DomainUpdate
from app.configuration.domains.service import DomainService
from app.configuration.domains.status import DomainStatus
from tests import engine
from tests.factories import DataProductFactory, DomainFactory, ExplorationFactory


def _remove_unknown_finalizer(service, id):
    with pytest.raises(HTTPException):
        service.remove_finalizer(id, "unknown")


def _update_unchanged(service, id):
    domain = service.db.get(DomainModel, id)
    service.update_domain(
        id,
        DomainUpdate(
            name=domain.name,
            description=domain.description,
            environment_ids=service.db.scalars(
                select(domain_environment_table.c.environment_id).where(
                    domain_environment_table.c.domain_id == id
                )
            ).all(),
        ),
    )


@pytest.mark.parametrize(
    ("finalizers", "call"),
    [
        ([], lambda service, id: service.ensure_assignable(id)),
        ([], lambda service, id: service.mark_for_deletion(id)),
        (["existing"], lambda service, id: service.add_finalizer(id, "existing")),
        (["existing"], _remove_unknown_finalizer),
        ([], _update_unchanged),
    ],
    ids=[
        "ensure_assignable",
        "mark_for_deletion",
        "add_finalizer",
        "remove_finalizer",
        "update_domain",
    ],
)
def test__get_locked__holds_the_domain_lock_until_commit(session, finalizers, call):
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


def test_ensure_assignable__lets_other_assignments_through(session):
    domain = DomainFactory()
    DomainService(session).ensure_assignable(domain.id)
    try:
        with engine.connect() as other:
            locked = other.scalar(
                select(DomainModel.id)
                .where(DomainModel.id == domain.id)
                .with_for_update(read=True, nowait=True)
            )
        assert locked == domain.id
    finally:
        session.rollback()


def test_reject_assignment_to_deleting_domain__new_data_product(session):
    domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["x"])
    with pytest.raises(IntegrityError, match="pending deletion"):
        DataProductFactory(domain=domain)
    session.rollback()


def test_reject_assignment_to_deleting_domain__moved_exploration(session):
    exploration = ExplorationFactory()
    deleting = DomainFactory(status=DomainStatus.DELETING, finalizers=["x"])
    exploration.domain_id = deleting.id
    with pytest.raises(IntegrityError, match="pending deletion"):
        session.flush()
    session.rollback()


def test_reject_assignment_to_deleting_domain__other_updates_allowed(session):
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
