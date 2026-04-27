from typing import Final

import factory
from faker import Faker
from sqlalchemy import select

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.model import Role
from app.authorization.roles.schema import Prototype
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from tests import test_session

faker: Final[Faker] = Faker()


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda _: faker.unique.name())
    scope = factory.Faker(
        "random_element", elements=("global", "data_product", "dataset")
    )
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

    @classmethod
    def admin(cls):
        return test_session.get(Role, ADMIN_UUID)

    @classmethod
    def data_product_owner(cls) -> Role:
        return test_session.scalar(
            select(Role)
            .where(Role.prototype == Prototype.OWNER)
            .where(Role.scope == "data_product")
        )

    @classmethod
    def dataset_owner(cls) -> Role:
        return test_session.scalar(
            select(Role)
            .where(Role.prototype == Prototype.OWNER)
            .where(Role.scope == "dataset")
        )
