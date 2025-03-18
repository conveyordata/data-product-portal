import factory

from app.core.authz.actions import AuthorizationAction
from app.roles.model import Role
from app.roles.schema import Prototype


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
