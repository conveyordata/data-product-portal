from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.groups.model import Group, GroupMembership, ensure_group_exists
from app.groups.schema_request import GroupCreate, GroupUpdate
from app.groups.schema_response import (
    GroupCreateResponse,
    GroupGet,
    GroupUpdateResponse,
)
from app.identities.model import ensure_identity_exists
from app.machine_users.model import MachineUser
from app.users.model import User


class GroupService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_memberships(self, group_id: UUID | None = None) -> list[GroupMembership]:
        query = select(GroupMembership)
        if group_id is not None:
            query = query.where(GroupMembership.group_id == group_id)

        return list(self.db.scalars(query).all())

    def add_member(self, group_id: UUID, member_identity_id: UUID) -> GroupMembership:
        ensure_group_exists(group_id, self.db)
        member = ensure_identity_exists(member_identity_id, self.db)

        if not isinstance(member, (User, MachineUser)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only users and machine users can be group members.",
            )

        if self.has_member(group_id, member_identity_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The identity is already a member of this group.",
            )

        membership = GroupMembership(
            group_id=group_id,
            member_identity_id=member_identity_id,
        )
        self.db.add(membership)
        self.db.flush()

        # Refresh Casbin graph after member addition
        authorizer = Authorization()
        authorizer.assign_global_group_membership(
            member_identity_id=member_identity_id,
            group_id=group_id,
        )
        authorizer.assign_resource_group_membership(
            member_identity_id=member_identity_id, group_id=group_id
        )

        return membership

    def remove_member(self, group_id: UUID, member_identity_id: UUID):
        membership = self.get_membership(group_id, member_identity_id)

        # Revoke the roles before removing the member
        authorizer = Authorization()
        authorizer.revoke_global_group_membership(
            member_identity_id=member_identity_id,
            group_id=group_id,
        )
        authorizer.revoke_resource_group_membership(
            member_identity_id=member_identity_id, group_id=group_id
        )

        self.db.delete(membership)
        self.db.flush()

    def delete_group(self, *, group_id: UUID) -> None:
        group = ensure_group_exists(group_id, self.db)

        # Removes assignments for users against this group
        authorizer = Authorization()
        for membership in self.list_memberships(group_id):
            authorizer.revoke_resource_group_membership(
                member_identity_id=membership.member_identity_id,
                group_id=group_id,
            )
            authorizer.revoke_global_group_membership(
                member_identity_id=membership.member_identity_id,
                group_id=group_id,
            )
        # Remove assignments where the group itself is the subject.
        authorizer.clear_assignments_for_user(user_id=group_id)

        self.db.delete(group)
        self.db.flush()

    def has_member(self, group_id: UUID, member_identity_id: UUID) -> bool:
        membership = self.db.get(
            GroupMembership,
            (group_id, member_identity_id),
        )
        return membership is not None

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
