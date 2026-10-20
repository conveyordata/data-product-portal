import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.configuration.domains.model import Domain as DomainModel
from app.configuration.domains.service import DomainService
from tests import engine
from tests.factories import DomainFactory


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
