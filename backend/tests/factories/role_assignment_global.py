import factory
from tests import test_session

from app.core.authz.authorization import Authorization
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.roles import ADMIN_UUID


class GlobalRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = GlobalRoleAssignment

    id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    role_id = factory.Faker("uuid4")
    decision = DecisionStatus.PENDING

    @factory.post_generation
    def sync_role(self, create, extracted, **kwargs):
        authorizer = Authorization()
        if self.role_id == ADMIN_UUID:
            authorizer.assign_admin_role(user_id=str(self.user_id))
        else:
            authorizer.assign_global_role(
                role_id=str(self.role_id), user_id=str(self.user_id)
            )
        test_session.commit()
