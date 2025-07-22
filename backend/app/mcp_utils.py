import logging
from functools import wraps
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_outputs.service import DataOutputService

# Import existing services for utility functions
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.datasets.service import DatasetService
from app.domains.service import DomainService

logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_CONFIG = {
    "server_name": "DataProductPortalMCPServer",
    "version": "1.0.0",
    "description": "MCP Server for Data Product Portal - Access data products, datasets, and marketplace",
    "max_results_per_query": 50,
    "default_search_limit": 20,
}


class EntityNotFoundError(Exception):
    """Raised when a requested entity is not found."""

    pass


class DataPortalMCPUtils:
    """Utility class for MCP server operations using existing services."""

    @staticmethod
    def validate_uuid(uuid_string: str) -> UUID:
        """Validate and convert string to UUID."""
        try:
            return UUID(uuid_string)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {uuid_string}")

    @staticmethod
    def get_entity_by_id(db: Session, entity_type: str, entity_id: str) -> Any:
        """
        Generic method to get any entity by ID using existing services.

        Args:
            db: Database session
            entity_type: Type of entity (data_product, dataset, data_output, domain)
            entity_id: ID of the entity

        Returns:
            The requested entity

        Raises:
            EntityNotFoundError: If entity is not found
            ValueError: If entity_type is invalid
        """
        uuid_id = DataPortalMCPUtils.validate_uuid(entity_id)

        # Use the same pattern as in mcp.py - services are instantiated with db
        if entity_type == "data_product":
            entity = DataProductService(db).get_data_product_by_id(
                data_product_id=uuid_id
            )
        elif entity_type == "dataset":
            entity = DatasetService(db).get_dataset_by_id(dataset_id=uuid_id)
        elif entity_type == "data_output":
            entity = DataOutputService(db).get_data_output_by_id(data_output_id=uuid_id)
        elif entity_type == "domain":
            entity = DomainService(db).get_domain_by_id(domain_id=uuid_id)
        else:
            raise ValueError(f"Invalid entity type: {entity_type}")

        if not entity:
            raise EntityNotFoundError(
                f"{entity_type.replace('_', ' ').title()} {entity_id} not found"
            )

        return entity

    @staticmethod
    def format_entity_summary(entity_type: str, entity: Any) -> Dict[str, Any]:
        """
        Format entity for summary display using existing Pydantic schemas.

        Args:
            entity_type: Type of entity
            entity: The entity object

        Returns:
            Formatted entity data
        """
        # Use the same schema names as in mcp.py
        try:
            if entity_type == "data_product":
                from app.data_products.schema_response import DataProductGet

                return DataProductGet.model_validate(entity).model_dump()
            elif entity_type == "dataset":
                from app.datasets.schema_response import DatasetGet

                return DatasetGet.model_validate(entity).model_dump()
            elif entity_type == "data_output":
                from app.data_outputs.schema_response import DataOutputGet

                return DataOutputGet.model_validate(entity).model_dump()
            elif entity_type == "domain":
                from app.domains.schema_response import DomainGet

                return DomainGet.model_validate(entity).model_dump()
            else:
                # Fallback to basic dict conversion
                return {
                    "id": str(entity.id),
                    "name": getattr(entity, "name", "Unknown"),
                }
        except Exception as e:
            logger.error(f"Error formatting {entity_type}: {e}")
            # Fallback to basic dict conversion
            return {"id": str(entity.id), "name": getattr(entity, "name", "Unknown")}

    @staticmethod
    def search_across_entities(
        db: Session, query: str, entity_types: Optional[list] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search across multiple entity types using existing service methods.

        Args:
            db: Database session
            query: Search query
            entity_types: List of entity types to search
            limit: Maximum results per entity type

        Returns:
            Search results organized by entity type
        """
        results = {}
        search_types = entity_types or [
            "data_products",
            "datasets",
            "data_outputs",
            "domains",
        ]
        # Search data products - use the same pattern as mcp.py
        if "data_products" in search_types:
            try:
                data_products = DataProductService(db).get_data_products(
                    search=query, limit=limit
                )
                results["data_products"] = [
                    DataPortalMCPUtils.format_entity_summary("data_product", dp)
                    for dp in data_products
                ]
            except Exception as e:
                logger.error(f"Error searching data products: {e}")
                results["data_products"] = []

        # Search datasets
        if "datasets" in search_types:
            try:
                datasets = DatasetService(db).get_datasets(search=query, limit=limit)
                results["datasets"] = [
                    DataPortalMCPUtils.format_entity_summary("dataset", ds)
                    for ds in datasets
                ]
            except Exception as e:
                logger.error(f"Error searching datasets: {e}")
                results["datasets"] = []

        # Search data outputs
        if "data_outputs" in search_types:
            try:
                data_outputs = DataOutputService(db).get_data_outputs(
                    search=query, limit=limit
                )
                results["data_outputs"] = [
                    DataPortalMCPUtils.format_entity_summary("data_output", do)
                    for do in data_outputs
                ]
            except Exception as e:
                logger.error(f"Error searching data outputs: {e}")
                results["data_outputs"] = []

        # Search domains
        if "domains" in search_types:
            try:
                domains = DomainService(db).get_domains(search=query, limit=limit)
                results["domains"] = [
                    DataPortalMCPUtils.format_entity_summary("domain", domain)
                    for domain in domains
                ]
            except Exception as e:
                logger.error(f"Error searching domains: {e}")
                results["domains"] = []

        return results

    @staticmethod
    def get_relationship_data(
        db: Session, entity_type: str, entity_id: str
    ) -> Dict[str, Any]:
        """
        Get relationship data for an entity using existing services.

        Args:
            db: Database session
            entity_type: Type of entity
            entity_id: ID of the entity

        Returns:
            Relationship data
        """
        uuid_id = DataPortalMCPUtils.validate_uuid(entity_id)
        relationships = {}

        if entity_type == "data_product":
            # Get related datasets
            try:
                datasets = DatasetService(db).get_datasets(data_product_id=uuid_id)
                relationships["datasets"] = [
                    DataPortalMCPUtils.format_entity_summary("dataset", ds)
                    for ds in datasets
                ]
            except Exception as e:
                logger.error(f"Error getting datasets for data product: {e}")
                relationships["datasets"] = []

            # Get related data outputs
            try:
                data_outputs = DataOutputService(db).get_data_outputs(
                    data_product_id=uuid_id
                )
                relationships["data_outputs"] = [
                    DataPortalMCPUtils.format_entity_summary("data_output", do)
                    for do in data_outputs
                ]
            except Exception as e:
                logger.error(f"Error getting data outputs for data product: {e}")
                relationships["data_outputs"] = []

        elif entity_type == "dataset":
            # Get related data products - assuming datasets have data_product_id
            try:
                dataset = DatasetService(db).get_dataset_by_id(dataset_id=uuid_id)
                if (
                    dataset
                    and hasattr(dataset, "data_product_id")
                    and dataset.data_product_id
                ):
                    data_product = DataProductService(db).get_data_product_by_id(
                        data_product_id=dataset.data_product_id
                    )
                    if data_product:
                        relationships["data_products"] = [
                            DataPortalMCPUtils.format_entity_summary(
                                "data_product", data_product
                            )
                        ]
                    else:
                        relationships["data_products"] = []
                else:
                    relationships["data_products"] = []
            except Exception as e:
                logger.error(f"Error getting data products for dataset: {e}")
                relationships["data_products"] = []

        elif entity_type == "domain":
            # Get data products in this domain
            try:
                data_products = DataProductService(db).get_data_products(
                    domain_id=uuid_id
                )
                relationships["data_products"] = [
                    DataPortalMCPUtils.format_entity_summary("data_product", dp)
                    for dp in data_products
                ]
            except Exception as e:
                logger.error(f"Error getting data products for domain: {e}")
                relationships["data_products"] = []

        return relationships


def with_db_session(func):
    """Decorator to provide database session to MCP tool functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with next(get_db_session()) as db:
                return func(db, *args, **kwargs)
        except EntityNotFoundError as e:
            return {"error": str(e)}
        except ValueError as e:
            return {"error": f"Validation error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

    return wrapper
