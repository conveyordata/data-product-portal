"""Tools for role assignments and user permissions across the portal."""

from typing import Any, Optional
from uuid import UUID

from fastmcp.dependencies import Depends
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse,
)
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.global_.schema import (
    GlobalRoleAssignmentResponse,
)
from app.authorization.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.authorization.role_assignments.output_port.schema import (
    OutputPortRoleAssignmentResponse as DatasetRoleAssignmentResponse,
)
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.mcp.deps import get_mcp_authenticated_user, get_user_db_session
from app.users.model import User as UserModel


def register_permission_tools(mcp) -> None:
    @mcp.tool(
        description="""
    Get role assignments for a user across the portal.
    Use get_current_user first to resolve 'me' or 'my' to a user ID.
    Requires authentication.

    Args:
        user_id: UUID of the user. Defaults to the currently authenticated user.
        scope_type: Filter by scope. Valid values: 'global' (portal-wide roles),
                    'data_product' (roles on specific data products),
                    'dataset' (roles on specific output ports). Leave empty to return all scopes.
        limit: Maximum number of role assignments to return.
    """
    )
    def get_user_roles(
        user_id: Optional[str] = None,
        scope_type: Optional[str] = None,
        limit: int = 50,
        db: Session = Depends(get_user_db_session),
        current_user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:

        target_user_id = user_id or str(current_user.id)

        global_roles: list[dict[str, Any]] = []
        data_product_roles: dict[str, list[dict[str, Any]]] = {}
        dataset_roles: dict[str, list[dict[str, Any]]] = {}

        if not scope_type or scope_type == "global":
            global_role_service = GlobalRoleAssignmentService(db)
            global_assignments = global_role_service.list_assignments(
                user_id=UUID(target_user_id)
            )
            global_roles = [
                GlobalRoleAssignmentResponse.model_validate(assignment).model_dump()
                for assignment in global_assignments[:limit]
            ]

        if not scope_type or scope_type == "data_product":
            data_product_role_service = DataProductRoleAssignmentService(db)
            dp_assignments = data_product_role_service.list_assignments(
                user_id=UUID(target_user_id)
            )

            for assignment in dp_assignments[:limit]:
                assignment_data = DataProductRoleAssignmentResponse.model_validate(
                    assignment
                ).model_dump()
                dp_id = str(assignment.data_product_id)
                if dp_id not in data_product_roles:
                    data_product_roles[dp_id] = []
                data_product_roles[dp_id].append(assignment_data)

        if not scope_type or scope_type == "dataset":
            dataset_role_service = DatasetRoleAssignmentService(db)
            dataset_assignments = dataset_role_service.list_assignments(
                user_id=UUID(target_user_id)
            )

            for assignment in dataset_assignments[:limit]:
                assignment_data = DatasetRoleAssignmentResponse.model_validate(
                    assignment
                ).model_dump()
                ds_id = str(assignment.output_port_id)
                if ds_id not in dataset_roles:
                    dataset_roles[ds_id] = []
                dataset_roles[ds_id].append(assignment_data)

        total_assignments = (
            len(global_roles)
            + sum(len(roles) for roles in data_product_roles.values())
            + sum(len(roles) for roles in dataset_roles.values())
        )

        return {
            "user_id": target_user_id,
            "is_current_user": target_user_id == str(current_user["id"]),
            "total_assignments": total_assignments,
            "roles": {
                "global": global_roles,
                "data_products": data_product_roles,
                "output_ports": dataset_roles,
            },
            "filters_applied": {
                "scope_type": scope_type,
            },
            "summary": {
                "global_roles_count": len(global_roles),
                "data_product_roles_count": len(data_product_roles),
                "dataset_roles_count": len(dataset_roles),
            },
        }

    @mcp.tool
    def get_resource_roles(
        resource_type: str,
        resource_id: str,
        limit: int = 50,
        db: Session = Depends(get_user_db_session),
    ) -> dict[str, Any]:
        """
        List all users and their roles on a specific data product or output port.

        Args:
            resource_type: Type of resource. Valid values: 'data_product' or 'dataset' (output ports use 'dataset').
            resource_id: UUID of the resource.
            limit: Maximum number of role assignments to return.
        """
        resource_uuid = UUID(resource_id)

        assignment_responses: list[dict[str, Any]] = []
        if resource_type == "data_product":
            assignments = DataProductRoleAssignmentService(db).list_assignments(
                data_product_id=resource_uuid
            )
            assignment_responses = [
                DataProductRoleAssignmentResponse.model_validate(
                    assignment
                ).model_dump()
                for assignment in assignments[:limit]
            ]
        elif resource_type == "dataset":
            assignments = DatasetRoleAssignmentService(db).list_assignments(
                dataset_id=resource_uuid
            )
            assignment_responses = [
                DatasetRoleAssignmentResponse.model_validate(assignment).model_dump()
                for assignment in assignments[:limit]
            ]
        else:
            return {
                "error": f"Invalid resource_type: {resource_type}.\
                    Must be 'data_product' or 'dataset'"
            }

        roles_by_type: dict[str, list[dict[str, Any]]] = {}
        users_with_roles: list[dict[str, Any]] = []

        for assignment_data in assignment_responses:
            role_info = assignment_data.get("role", {})
            role_name = (
                role_info.get("name", "Unknown")
                if isinstance(role_info, dict)
                else "Unknown"
            )
            if role_name not in roles_by_type:
                roles_by_type[role_name] = []
            roles_by_type[role_name].append(assignment_data)

            users_with_roles.append(
                {
                    "user_id": assignment_data.get("user_id"),
                    "role_name": role_name,
                    "assignment_id": assignment_data.get("id"),
                    "created_at": assignment_data.get("created_at"),
                }
            )

        return {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "total_assignments": len(assignment_responses),
            "roles_by_type": roles_by_type,
            "users_with_roles": users_with_roles,
            "summary": {
                "unique_roles": list(roles_by_type.keys()),
                "total_users": len(users_with_roles),
            },
        }
