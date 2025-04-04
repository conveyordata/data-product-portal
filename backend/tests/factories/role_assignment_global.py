import factory

from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment


class GlobalRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = GlobalRoleAssignment

    id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    role_id = factory.Faker("uuid4")
    decision = DecisionStatus.PENDING
