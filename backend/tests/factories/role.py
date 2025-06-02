import factory
from tests import test_session

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.roles import ADMIN_UUID
from app.roles.model import Role
from app.roles.schema import Prototype, Scope


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role

    id = factory.Faker("uuid4")
    name = factory.Faker("job")
    scope = factory.Faker(
        "random_element", elements=("global", "data_product", "dataset")
    )
    prototype = Prototype.CUSTOM
    description = factory.Faker("text")
    permissions = factory.Faker(
        "random_elements", elements=list(map(int, AuthorizationAction)), unique=True
    )

    @factory.post_generation
    def sync_role(self, create, extracted, **kwargs):
        authorizer = Authorization()
        if self.id != ADMIN_UUID:
            authorizer.sync_role_permissions(
                role_id=str(self.id), actions=self.permissions
            )
        test_session.commit()
