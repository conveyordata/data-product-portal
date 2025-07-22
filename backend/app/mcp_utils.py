"""
MCP Server Configuration and Utilities for Data Product Portal
"""

# import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload, raiseload

from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_products.model import DataProduct as DataProductModel
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import get_db_session
from app.datasets.model import Dataset as DatasetModel
from app.events.model import Event as EventModel

# from app.platforms.model import Platform as PlatformModel
from app.role_assignments.enums import DecisionStatus
from app.users.model import User as UserModel


class DataPortalMCPUtils:
    """Utility class for MCP server operations"""

    @staticmethod
    def get_db() -> Session:
        """Get database session"""
        return next(get_db_session())

    @staticmethod
    def format_entity_summary(entity: Any, entity_type: str) -> Dict[str, Any]:
        """Format entity for consistent API responses"""
        base_info = {
            "id": str(entity.id),
            "name": entity.name,
            "namespace": getattr(entity, "namespace", None),
            "description": getattr(entity, "description", None),
            "type": entity_type,
            "created_on": (
                entity.created_on.isoformat()
                if hasattr(entity, "created_on") and entity.created_on
                else None
            ),
            "updated_on": (
                entity.updated_on.isoformat()
                if hasattr(entity, "updated_on") and entity.updated_on
                else None
            ),
        }

        # Add entity-specific fields
        if entity_type == "data_product":
            base_info.update(
                {
                    "status": entity.status.value if entity.status else None,
                    "domain": entity.domain.name if entity.domain else None,
                    "user_count": getattr(entity, "user_count", 0),
                    "dataset_count": getattr(entity, "dataset_count", 0),
                    "data_outputs_count": getattr(entity, "data_outputs_count", 0),
                }
            )
        elif entity_type == "dataset":
            base_info.update(
                {
                    "status": entity.status.value if entity.status else None,
                    "access_type": (
                        entity.access_type.value if entity.access_type else None
                    ),
                    "domain": entity.domain.name if entity.domain else None,
                    "data_product_count": getattr(entity, "data_product_count", 0),
                }
            )
        elif entity_type == "data_output":
            base_info.update(
                {
                    "status": entity.status.value if entity.status else None,
                    "platform_id": str(entity.platform_id),
                    "service_id": str(entity.service_id),
                    "owner": entity.owner.name if entity.owner else None,
                }
            )

        return base_info

    @staticmethod
    def get_activity_feed(limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity across the data portal"""
        db = DataPortalMCPUtils.get_db()

        try:
            # Get recent events
            recent_events = (
                db.scalars(
                    select(EventModel)
                    .order_by(EventModel.created_on.desc())
                    .limit(limit)
                )
                .unique()
                .all()
            )

            activities = []
            for event in recent_events:
                activities.append(
                    {
                        "id": str(event.id),
                        "type": event.type.value if event.type else None,
                        "reference_entity": (
                            event.reference_entity.value
                            if event.reference_entity
                            else None
                        ),
                        "reference_entity_id": (
                            str(event.reference_entity_id)
                            if event.reference_entity_id
                            else None
                        ),
                        "description": event.description,
                        "created_on": (
                            event.created_on.isoformat() if event.created_on else None
                        ),
                        "created_by": (
                            event.created_by.email if event.created_by else None
                        ),
                    }
                )

            return activities
        finally:
            db.close()

    @staticmethod
    def get_trending_data(days: int = 7) -> Dict[str, Any]:
        """Get trending data products and datasets"""
        db = DataPortalMCPUtils.get_db()

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Most accessed datasets (based on data product links)
            trending_datasets = (
                db.execute(
                    select(
                        DatasetModel.id,
                        DatasetModel.name,
                        DatasetModel.namespace,
                        func.count(DataProductDatasetAssociation.id).label(
                            "access_count"
                        ),
                    )
                    .join(DataProductDatasetAssociation)
                    .where(
                        and_(
                            DataProductDatasetAssociation.approved_on >= cutoff_date,
                            DataProductDatasetAssociation.status
                            == DecisionStatus.APPROVED,
                        )
                    )
                    .group_by(
                        DatasetModel.id, DatasetModel.name, DatasetModel.namespace
                    )
                    .order_by(func.count(DataProductDatasetAssociation.id).desc())
                    .limit(10)
                )
                .unique()
                .all()
            )

            # Most active data products (based on recent updates)
            active_products = (
                db.execute(
                    select(
                        DataProductModel.id,
                        DataProductModel.name,
                        DataProductModel.namespace,
                        func.count(EventModel.id).label("activity_count"),
                    )
                    .join(
                        EventModel,
                        EventModel.reference_entity_id == DataProductModel.id,
                    )
                    .where(EventModel.created_on >= cutoff_date)
                    .group_by(
                        DataProductModel.id,
                        DataProductModel.name,
                        DataProductModel.namespace,
                    )
                    .order_by(func.count(EventModel.id).desc())
                    .limit(10)
                )
                .unique()
                .all()
            )

            return {
                "period_days": days,
                "trending_datasets": [
                    {
                        "id": str(item.id),
                        "name": item.name,
                        "namespace": item.namespace,
                        "access_count": item.access_count,
                    }
                    for item in trending_datasets
                ],
                "active_data_products": [
                    {
                        "id": str(item.id),
                        "name": item.name,
                        "namespace": item.namespace,
                        "activity_count": item.activity_count,
                    }
                    for item in active_products
                ],
            }
        finally:
            db.close()

    @staticmethod
    def search_across_entities(
        query: str, entity_types: Optional[List[str]] = None, limit: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Universal search across data products, datasets, and data outputs"""
        if entity_types is None:
            entity_types = ["data_products", "datasets", "data_outputs"]

        db = DataPortalMCPUtils.get_db()
        results = {}

        try:
            search_pattern = f"%{query}%"

            if "data_products" in entity_types:
                data_products = (
                    db.scalars(
                        select(DataProductModel)
                        .options(
                            joinedload(DataProductModel.dataset_links).raiseload("*"),
                            joinedload(DataProductModel.assignments).raiseload("*"),
                            joinedload(DataProductModel.data_outputs).raiseload("*"),
                        )
                        .where(
                            or_(
                                DataProductModel.name.ilike(search_pattern),
                                DataProductModel.description.ilike(search_pattern),
                                DataProductModel.namespace.ilike(search_pattern),
                            )
                        )
                        .limit(limit)
                    )
                    .unique()
                    .all()
                )

                results["data_products"] = [
                    DataPortalMCPUtils.format_entity_summary(dp, "data_product")
                    for dp in data_products
                ]

            if "datasets" in entity_types:
                datasets = db.scalars(
                    select(DatasetModel)
                    .options(
                        joinedload(DatasetModel.data_product_links)
                        .joinedload(DataProductDatasetAssociation.data_product)
                        .raiseload("*"),
                        joinedload(DatasetModel.data_output_links)
                        .joinedload(DataOutputDatasetAssociation.data_output)
                        .options(
                            joinedload(DataOutputModel.configuration),
                            joinedload(DataOutputModel.owner),
                            raiseload("*"),
                        ),
                    )
                    .where(
                        or_(
                            DatasetModel.name.ilike(search_pattern),
                            DatasetModel.description.ilike(search_pattern),
                            DatasetModel.namespace.ilike(search_pattern),
                        )
                    )
                    .limit(limit)
                ).all()

                results["datasets"] = [
                    DataPortalMCPUtils.format_entity_summary(ds, "dataset")
                    for ds in datasets
                ]

            if "data_outputs" in entity_types:
                data_outputs = (
                    db.scalars(
                        select(DataOutputModel)
                        .options(
                            joinedload(DataOutputModel.environment_configurations),
                            joinedload(DataOutputModel.dataset_links)
                            .joinedload(DataOutputDatasetAssociation.dataset)
                            .raiseload("*"),
                        )
                        .where(
                            or_(
                                DataOutputModel.name.ilike(search_pattern),
                                DataOutputModel.description.ilike(search_pattern),
                                DataOutputModel.namespace.ilike(search_pattern),
                            )
                        )
                        .limit(limit)
                    )
                    .unique()
                    .all()
                )

                results["data_outputs"] = [
                    DataPortalMCPUtils.format_entity_summary(do, "data_output")
                    for do in data_outputs
                ]

            return results
        finally:
            db.close()

    @staticmethod
    def get_user_recommendations(user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations for a user"""
        db = DataPortalMCPUtils.get_db()

        try:
            user = db.get(UserModel, user_id)
            if not user:
                return {"error": "User not found"}

            # Get user's current data products
            user_data_products = (
                db.scalars(
                    select(DataProductModel)
                    .join(DataProductModel.assignments)
                    .where(
                        and_(
                            DataProductModel.assignments.any(user_id=user.id),
                            DataProductModel.assignments.any(
                                decision=DecisionStatus.APPROVED
                            ),
                        )
                    )
                )
                .unique()
                .all()
            )

            # Get domains user is active in
            user_domains = set(
                dp.domain_id for dp in user_data_products if dp.domain_id
            )

            # Recommend datasets from same domains that user doesn't have access to
            recommended_datasets = []
            if user_domains:
                datasets = (
                    db.scalars(
                        select(DatasetModel)
                        .where(DatasetModel.domain_id.in_(user_domains))
                        .limit(limit)
                    )
                    .unique()
                    .all()
                )

                for dataset in datasets:
                    # Check if user already has access
                    has_access = any(
                        db.scalar(
                            select(DataProductDatasetAssociation).where(
                                and_(
                                    DataProductDatasetAssociation.data_product_id
                                    == dp.id,
                                    DataProductDatasetAssociation.dataset_id
                                    == dataset.id,
                                    DataProductDatasetAssociation.status
                                    == DecisionStatus.APPROVED,
                                )
                            )
                        )
                        for dp in user_data_products
                    )

                    if not has_access:
                        recommended_datasets.append(
                            DataPortalMCPUtils.format_entity_summary(dataset, "dataset")
                        )

            # Recommend popular datasets
            popular_datasets = (
                db.execute(
                    select(
                        DatasetModel,
                        func.count(DataProductDatasetAssociation.id).label(
                            "popularity"
                        ),
                    )
                    .join(DataProductDatasetAssociation)
                    .where(
                        DataProductDatasetAssociation.status == DecisionStatus.APPROVED
                    )
                    .group_by(DatasetModel.id)
                    .order_by(func.count(DataProductDatasetAssociation.id).desc())
                    .limit(limit)
                )
                .unique()
                .all()
            )

            return {
                "user_id": user_id,
                "recommended_datasets": recommended_datasets[:limit],
                "popular_datasets": [
                    {
                        **DataPortalMCPUtils.format_entity_summary(
                            item.DatasetModel, "dataset"
                        ),
                        "popularity_score": item.popularity,
                    }
                    for item in popular_datasets
                ],
            }
        finally:
            db.close()


# Configuration constants
MCP_CONFIG = {
    "server_name": "DataProductPortalMCPServer",
    "version": "1.0.0",
    "description": "MCP Server for Data Product Portal - enabling AI agents to interact with data products, datasets, and marketplace",
    "capabilities": [
        "data_discovery",
        "marketplace_browsing",
        "lineage_tracking",
        "access_management",
        "platform_configuration",
        "activity_monitoring",
    ],
    "supported_entities": [
        "data_products",
        "datasets",
        "data_outputs",
        "domains",
        "platforms",
        "users",
    ],
}


# Error handling utilities
class MCPError(Exception):
    """Base MCP error class"""

    pass


class EntityNotFoundError(MCPError):
    """Entity not found error"""

    pass


class AccessDeniedError(MCPError):
    """Access denied error"""

    pass


def handle_mcp_error(func):
    """Decorator for error handling in MCP tools"""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EntityNotFoundError as e:
            return {"error": f"Entity not found: {str(e)}"}
        except AccessDeniedError as e:
            return {"error": f"Access denied: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    return wrapper
