from typing import Iterable, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.groups.model import Group, GroupMembership, ensure_group_exists
from app.groups.schema_request import GroupCreate, GroupUpdate
from app.groups.schema_response import (
    GroupCreateResponse,
    GroupGet,
    GroupUpdateResponse,
)
from app.identities.model import Identity
from app.identities.type import IdentityType


class GroupService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.authorizer = Authorization()

    def list_memberships(self, group_id: UUID | None = None) -> list[GroupMembership]:
        query = select(GroupMembership).order_by(
            asc(GroupMembership.member_identity_id)
        )
        if group_id is not None:
            query = query.where(GroupMembership.group_id == group_id)

        return list(self.db.scalars(query).all())

    def get_members(self, group_id: UUID) -> Sequence[GroupMembership]:
        ensure_group_exists(group_id, self.db)
        return self.list_memberships(group_id)

    def add_members(
        self,
        group_id: UUID,
        member_identity_ids: list[UUID],
    ) -> None:
        """
        Adds members in batch to a group. Already existing members are ignored.
        """
        requested_ids = set(member_identity_ids)
        if not requested_ids:
            return

        self._lock_group(group_id)
        self._validate_member_identities(requested_ids)

        inserted_ids = self._insert_member_ids(group_id, requested_ids)
        self._add_members_auth(group_id, inserted_ids)

    def remove_members(
        self,
        group_id: UUID,
        member_identity_ids: list[UUID],
    ) -> None:
        """
        Removes members in batch to a group. Silently ignores missing members.
        """
        requested_ids = set(member_identity_ids)
        if not requested_ids:
            return

        self._lock_group(group_id)

        removed_ids = self._remove_member_ids(group_id, requested_ids)
        self._remove_members_auth(group_id, removed_ids)

    def replace_members(
        self,
        group_id: UUID,
        member_identity_ids: list[UUID],
    ) -> None:
        """
        Allows a full replacement of the members of a group.
        """
        requested_ids = set(member_identity_ids)
        if not requested_ids:
            return

        self._lock_group(group_id)
        self._validate_member_identities(requested_ids)

        current_ids = set(
            self.db.scalars(
                select(GroupMembership.member_identity_id).where(
                    GroupMembership.group_id == group_id,
                )
            ).all()
        )

        ids_to_add = requested_ids - current_ids
        ids_to_remove = current_ids - requested_ids

        inserted_ids = (
            self._insert_member_ids(group_id, ids_to_add) if ids_to_add else []
        )
        removed_ids = (
            self._remove_member_ids(group_id, ids_to_remove) if ids_to_remove else []
        )

        self._add_members_auth(group_id, inserted_ids)
        self._remove_members_auth(group_id, removed_ids)

    def delete_group(self, *, group_id: UUID) -> None:
        group = ensure_group_exists(group_id, self.db)

        # Removes assignments for users against this group
        self._remove_members_auth(
            group_id,
            (
                membership.member_identity_id
                for membership in self.list_memberships(group_id)
            ),
        )
        # Remove assignments where the group itself is the subject.
        self.authorizer.clear_assignments_for_user(user_id=group_id)

        self.db.delete(group)
        self.db.flush()

    def get_membership(
        self, group_id: UUID, member_identity_id: UUID
    ) -> GroupMembership:
        membership = self.db.get(
            GroupMembership,
            (group_id, member_identity_id),
        )
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found.",
            )
        return membership

    def get_groups_ids_identity_is_member_of(self, identity_id: UUID) -> list[UUID]:
        return list(
            self.db.scalars(
                select(GroupMembership.group_id).where(
                    GroupMembership.member_identity_id == identity_id
                )
            ).all()
        )

    def get_groups(self) -> Sequence[GroupGet]:
        return self.db.scalars(
            select(Group).order_by(asc(Group.display_name), asc(Group.external_id))
        ).all()

    def get_group(self, group_id: UUID) -> GroupGet:
        return ensure_group_exists(group_id, self.db)

    def create_group(self, group: GroupCreate) -> GroupCreateResponse:
        self._ensure_external_id_available(group.external_id)
        group_model = Group(**group.parse_pydantic_schema())
        self.db.add(group_model)
        self.db.flush()

        return GroupCreateResponse(id=group_model.id)

    def update_group(self, group_id: UUID, group: GroupUpdate) -> GroupUpdateResponse:
        current_group = ensure_group_exists(group_id, self.db)
        current_group.display_name = group.display_name
        self.db.flush()
        return GroupUpdateResponse(id=current_group.id)

    def _ensure_external_id_available(self, external_id: str) -> None:
        query = select(Group.id).where(Group.external_id == external_id)
        if self.db.scalar(query) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A group with this external ID already exists.",
            )

    def _validate_member_identities(
        self,
        member_identity_ids: set[UUID],
    ) -> None:
        """
        Validates a list of member identity IDs to ensure they exist and correspond to
        users or machine users.

        For performance reasons, only one query is performed to check the validity
        of both conditions.
        """
        valid_count = self.db.scalar(
            select(func.count(Identity.id)).where(
                Identity.id.in_(member_identity_ids),
                Identity.type.in_(
                    (
                        IdentityType.USER.value,
                        IdentityType.MACHINE_USER.value,
                    )
                ),
            )
        )
        if valid_count != len(member_identity_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "All member identities must exist and be users or machine users."
                ),
            )

    def _add_members_auth(
        self, group_id: UUID, member_identity_ids: Iterable[UUID]
    ) -> None:
        for member_identity_id in member_identity_ids:
            self.authorizer.assign_global_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
            )
            self.authorizer.assign_resource_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
            )

    def _remove_members_auth(
        self, group_id: UUID, member_identity_ids: Iterable[UUID]
    ) -> None:
        for member_identity_id in member_identity_ids:
            self.authorizer.revoke_global_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
            )
            self.authorizer.revoke_resource_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
            )

    def _insert_member_ids(
        self, group_id: UUID, member_identity_ids: set[UUID]
    ) -> Sequence[UUID]:
        """
        Inserts a list of member identity IDs into the group_memberships table.
        Already existing members are ignored.
        """
        return self.db.scalars(
            insert(GroupMembership)
            .values(
                [
                    {
                        "group_id": group_id,
                        "member_identity_id": member_identity_id,
                    }
                    for member_identity_id in member_identity_ids
                ]
            )
            .on_conflict_do_nothing(
                index_elements=[
                    GroupMembership.group_id,
                    GroupMembership.member_identity_id,
                ]
            )
            .returning(GroupMembership.member_identity_id)
        ).all()

    def _remove_member_ids(
        self, group_id: UUID, member_identity_ids: set[UUID]
    ) -> Sequence[UUID]:
        return self.db.scalars(
            delete(GroupMembership)
            .where(
                GroupMembership.group_id == group_id,
                GroupMembership.member_identity_id.in_(member_identity_ids),
            )
            .returning(GroupMembership.member_identity_id)
        ).all()

    def _lock_group(self, group_id: UUID) -> None:
        locked_group_id = self.db.scalar(
            select(Group.id).where(Group.id == group_id).with_for_update(of=Group)
        )
        if locked_group_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} does not exist",
            )
