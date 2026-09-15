from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.groups.model import Group, GroupMembership


class GroupService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_memberships(self) -> list[GroupMembership]:
        return list(self.db.scalars(select(GroupMembership)).all())

    def list_assigned_data_products(self) -> dict[UUID, set[UUID]]:
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