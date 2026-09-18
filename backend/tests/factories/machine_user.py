import factory
from faker import Faker

from app.machine_users.model import MachineUser
from tests.factories.identity import IdentityFactory

fake = Faker()


class MachineUserFactory(IdentityFactory):
    class Meta:
        model = MachineUser

    display_name = factory.Sequence(lambda n: f"Machine USer {n}")
