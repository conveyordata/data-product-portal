from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.users.service import UserService
from tests.factories import (
    GroupFactory,
    GroupMembershipFactory,
    UserFactory,
)

from sqlalchemy import select

from app.core.authz import Authorization
from app.users.model import User


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


    def test_create_users_batch__creates_all_valid_users(self, session):
        result = UserService(session).create_users_batch(
            [
                {
                    "email": "first@example.com",
                    "external_id": "first-user",
                    "first_name": "First",
                    "last_name": "User",
                },
                {
                    "email": "second@example.com",
                    "external_id": "second-user",
                    "first_name": "Second",
                    "last_name": "User",
                },
            ]
        )

        users = session.scalars(select(User).where(User.id.in_(result.ids))).all()

        assert len(result.ids) == 2
        assert result.errors == []
        assert {user.external_id for user in users} == {
            "first-user",
            "second-user",
        }

    def test_create_users_batch__skips_schema_invalid_items(self, session):
        invalid_item = {
            "email": "not-an-email",
            "external_id": "invalid-user",
            "first_name": "Invalid",
            "last_name": "User",
        }

        result = UserService(session).create_users_batch(
            [
                {
                    "email": "valid@example.com",
                    "external_id": "valid-user",
                    "first_name": "Valid",
                    "last_name": "User",
                },
                invalid_item,
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].item == invalid_item
        assert result.errors[0].errors

    def test_create_users_batch__reports_existing_email_and_external_id(
        self, session
    ):
        UserFactory(
            email="existing@example.com",
            external_id="existing-user",
        )

        result = UserService(session).create_users_batch(
            [
                {
                    "email": "existing@example.com",
                    "external_id": "existing-user",
                    "first_name": "Duplicate",
                    "last_name": "User",
                }
            ]
        )

        assert result.ids == []
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A user with this email already exists.",
            "A user with this external ID already exists.",
        ]

    def test_create_users_batch__rejects_later_request_duplicates(self, session):
        result = UserService(session).create_users_batch(
            [
                {
                    "email": "duplicate@example.com",
                    "external_id": "duplicate-user",
                    "first_name": "First",
                    "last_name": "User",
                },
                {
                    "email": "duplicate@example.com",
                    "external_id": "duplicate-user",
                    "first_name": "Second",
                    "last_name": "User",
                },
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A user with this email already exists.",
            "A user with this external ID already exists.",
        ]

        created_user = session.get(User, result.ids[0])
        assert created_user is not None
        assert created_user.first_name == "First"

    def test_remove_users_batch__removes_matching_users(self, session):
        first = UserFactory()
        second = UserFactory()
        retained = UserFactory()

        UserService(session).remove_users_batch([first.id, second.id])

        assert session.get(User, first.id) is None
        assert session.get(User, second.id) is None
        assert session.get(User, retained.id) is not None

    def test_remove_users_batch__ignores_unknown_and_wrong_identity_type_ids(
        self, session
    ):
        user = UserFactory()
        group = GroupFactory()

        UserService(session).remove_users_batch([user.id, group.id, uuid4()])

        assert session.get(User, user.id) is None
        assert group in session

    def test_remove_users_batch__clears_only_deleted_users_authorization(
        self,
        authorizer: Authorization,
        session,
    ):
        removed = UserFactory()
        retained = UserFactory()

        authorizer.assign_resource_role(
            user_id=removed.id,
            role_id="resource-role",
            resource_id="resource",
        )
        authorizer.assign_domain_role(
            user_id=removed.id,
            role_id="domain-role",
            domain_id="domain",
        )
        authorizer.assign_global_role(
            user_id=removed.id,
            role_id="global-role",
        )
        authorizer.assign_global_role(
            user_id=retained.id,
            role_id="retained-role",
        )

        UserService(session).remove_users_batch([removed.id])

        assert not authorizer.has_resource_role(
            user_id=removed.id,
            role_id="resource-role",
            resource_id="resource",
        )
        assert not authorizer.has_domain_role(
            user_id=removed.id,
            role_id="domain-role",
            domain_id="domain",
        )
        assert not authorizer.has_global_role(
            user_id=removed.id,
            role_id="global-role",
        )
        assert authorizer.has_global_role(
            user_id=retained.id,
            role_id="retained-role",
        )
