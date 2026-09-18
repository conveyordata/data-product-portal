from sqlalchemy import select

from app.groups.model import Group
from app.identities.model import Identity
from app.machine_users.model import MachineUser
from app.users.model import User


class TestIdentityModel:
    def test_loads_polymorphic_identity_subtypes(self, session):
        user = User(
            external_id="user-1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
        )
        group = Group(
            external_id="group-1",
            display_name="Test Group",
        )
        machine_user = MachineUser(
            external_id="machine-1",
            display_name="Test Machine User",
        )
        session.add_all([user, group, machine_user])
        session.flush()

        ids = {user.id, group.id, machine_user.id}
        session.expunge_all()

        identities = {
            identity.id: identity
            for identity in session.scalars(
                select(Identity).where(Identity.id.in_(ids))
            ).all()
        }

        assert isinstance(identities[user.id], User)
        assert isinstance(identities[group.id], Group)
        assert isinstance(identities[machine_user.id], MachineUser)
