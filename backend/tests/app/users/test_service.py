from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.users.service import UserService
from tests.factories import (
    GroupFactory,
    GroupMembershipFactory,
    UserFactory,
)


class TestUserService:
    def test_get_groups__returns_groups_ordered_by_display_name_and_external_id(
        self,
        session,
    ):
        user = UserFactory()
        second = GroupFactory(
            display_name="Engineering",
            external_id="engineering-b",
        )
        first = GroupFactory(
            display_name="Engineering",
            external_id="engineering-a",
        )
        third = GroupFactory(
            display_name="Finance",
            external_id="finance",
        )
        other_group = GroupFactory()

        GroupMembershipFactory(group=second, member=user)
        GroupMembershipFactory(group=first, member=user)
        GroupMembershipFactory(group=third, member=user)

        groups = UserService(session).get_groups(user.id)

        assert list(groups) == [first, second, third]
        assert other_group not in groups

    def test_get_groups__user_without_groups_returns_empty_sequence(self, session):
        user = UserFactory()

        groups = UserService(session).get_groups(user.id)

        assert list(groups) == []

    def test_get_groups__unknown_user_raises_not_found(self, session):
        with pytest.raises(HTTPException) as exc_info:
            UserService(session).get_groups(uuid4())

        assert exc_info.value.status_code == 404
