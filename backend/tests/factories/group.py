import factory
from faker import Faker

from app.groups.model import Group, GroupMembership
from .identity import IdentityFactory
from .user import UserFactory

fake = Faker()


class GroupFactory(IdentityFactory):
    class Meta:
        model = Group

    display_name = factory.Sequence(lambda n: f"Group {n}")


class GroupMembershipFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = GroupMembership

    group = factory.SubFactory(GroupFactory)
    member = factory.SubFactory(UserFactory)