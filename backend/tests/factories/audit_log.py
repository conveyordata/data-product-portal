import factory
from tests.factories.user import UserFactory

from app.audit.model import AuditLog


class AuditLogFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AuditLog

    id = factory.Faker("uuid4")
    user = factory.SubFactory(UserFactory)
    subject_id = factory.Faker("uuid4")
    target_id = factory.Faker("uuid4")
    status_code = 200
    action = "test"
