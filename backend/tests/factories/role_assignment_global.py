import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.model import GlobalRoleAssignment
from app.authorization.roles import ADMIN_UUID
from app.core.authz.authorization import CasbinPolicies


class GlobalRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = GlobalRoleAssignment

    id = factory.Faker("uuid4")
    identity_id = factory.Faker("uuid4")
    role_id = factory.Faker("uuid4")
    decision = DecisionStatus.APPROVED

    @factory.post_generation
    def sync_role(self, create, extracted, **kwargs):
        if self.decision == DecisionStatus.APPROVED:
            policies = CasbinPolicies()
            if self.role_id == ADMIN_UUID:
                policies.assign_admin_role(user_id=str(self.identity_id))
            else:
                policies.assign_global_role(
                    role_id=str(self.role_id),
                    user_id=str(self.identity_id),
                )
