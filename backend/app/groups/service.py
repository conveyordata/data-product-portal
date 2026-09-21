from collections import defaultdict
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.authz import Authorization
from app.groups.model import Group, GroupMembership, ensure_group_exists
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

    def list_all_assigned_data_products(self) -> dict[UUID, set[UUID]]:
        rows = self.db.execute(
            select(
                DataProductRoleAssignment.identity_id,
                DataProductRoleAssignment.data_product_id,
            )
            .join(Group, Group.id == DataProductRoleAssignment.identity_id)
            .where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        ).all()

        assignments: dict[UUID, set[UUID]] = defaultdict(set)
        for group_id, data_product_id in rows:
            assignments[group_id].add(data_product_id)

        return assignments

    def list_assigned_data_products(self, group_id: UUID) -> Sequence[UUID]:
        return self.db.scalars(
            select(DataProductRoleAssignment.data_product_id)
            .join(Group, Group.id == DataProductRoleAssignment.identity_id)
            .where(
                DataProductRoleAssignment.decision == DecisionStatus.APPROVED,
                Group.id == group_id,
            )
        ).all()

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

        for data_product_id in self.list_assigned_data_products(group_id):
            authorizer.assign_resource_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
                resource_id=data_product_id,
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

        for data_product_id in self.list_assigned_data_products(group_id):
            authorizer.revoke_resource_group_membership(
                member_identity_id=member_identity_id,
                group_id=group_id,
                resource_id=data_product_id,
            )

        self.db.delete(membership)
        self.db.flush()

    def delete_group(self, *, group_id: UUID):
        group = ensure_group_exists(group_id, self.db)
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

    def get_group(self, group_id: UUID) -> Group:
        return ensure_group_exists(group_id, self.db)

    def add_data_product_membership_edges(
        self,
        group_id: UUID,
        data_product_id: UUID,
    ) -> None:
        authorizer = Authorization()
        for membership in self.list_memberships(group_id):
            authorizer.assign_resource_group_membership(
                member_identity_id=membership.member_identity_id,
                group_id=group_id,
                resource_id=data_product_id,
            )

    def remove_data_product_membership_edges(
        self,
        group_id: UUID,
        data_product_id: UUID,
    ) -> None:
        authorizer = Authorization()
        for membership in self.list_memberships(group_id):
            authorizer.revoke_resource_group_membership(
                member_identity_id=membership.member_identity_id,
                group_id=group_id,
                resource_id=data_product_id,
            )

    def is_group(self, identity_id: UUID) -> bool:
        return self.db.get(Group, identity_id) is not None
