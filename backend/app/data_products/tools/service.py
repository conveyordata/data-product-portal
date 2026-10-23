from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core import context
from app.core.webhooks.events import ToolEnvironmentConfigurationAppliedEvent
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import ensure_data_product_exists
from app.data_products.tools.model import Tool as ToolModel
from app.data_products.tools.model import ToolEnvironmentOverride, ensure_tool_exists
from app.data_products.tools.schema_request import (
    CreateToolRequest,
    UpdateToolEnvironmentConfigurationRequest,
)
from app.data_products.tools.schema_response import (
    EnvironmentPropertyValue,
    OverridablePropertyConfiguration,
    ToolEnvironmentConfiguration,
)
from app.plugins.platform import ToolType
from app.plugins.registry import plugin_registry


class ToolService:
    def __init__(self, db: Session):
        self.db = db

    def get_tools(self, data_product_id: UUID) -> Sequence[ToolModel]:
        ensure_data_product_exists(data_product_id, self.db)
        return self.db.scalars(
            select(ToolModel)
            .filter_by(data_product_id=data_product_id)
            .order_by(ToolModel.name)
        ).all()

    def get_tool(self, data_product_id: UUID, id: UUID) -> ToolModel:
        return ensure_tool_exists(id, self.db, data_product_id)

    def create_tool(
        self, data_product_id: UUID, request: CreateToolRequest
    ) -> ToolModel:
        ensure_data_product_exists(data_product_id, self.db)
        tool_type = plugin_registry.tool_type(request.platform_key, request.tool_type)
        tool = ToolModel(
            name=request.name,
            description=request.description,
            data_product_id=data_product_id,
            platform_key=request.platform_key,
            tool_type=request.tool_type,
            base_values={
                **{p.name: p.default for p in tool_type.overridable_properties},
                **self._validated(tool_type, request.base_values),
            },
        )
        self.db.add(tool)
        self.db.flush()
        return tool

    def delete_tool(self, data_product_id: UUID, id: UUID) -> None:
        self.db.delete(ensure_tool_exists(id, self.db, data_product_id))
        self.db.flush()

    def get_environment_configuration(
        self, data_product_id: UUID, id: UUID
    ) -> ToolEnvironmentConfiguration:
        tool = ensure_tool_exists(id, self.db, data_product_id)
        tool_type = plugin_registry.tool_type(tool.platform_key, tool.tool_type)
        environments = self._data_product(data_product_id).environments
        overrides = {o.environment_id: o.values for o in tool.overrides}
        properties = []
        for prop in tool_type.overridable_properties:
            base_value = tool.base_values.get(prop.name, prop.default)
            environment_values = []
            for declaration in environments:
                override = overrides.get(declaration.environment_id, {}).get(prop.name)
                environment_values.append(
                    EnvironmentPropertyValue(
                        id=declaration.environment.id,
                        name=declaration.environment.name,
                        acronym=declaration.environment.acronym,
                        override=override,
                        effective_value=override or base_value,
                    )
                )
            properties.append(
                OverridablePropertyConfiguration(
                    name=prop.name,
                    label=prop.label,
                    allowed_values=prop.allowed_values,
                    default=prop.default,
                    base_value=base_value,
                    environments=environment_values,
                )
            )
        return ToolEnvironmentConfiguration(properties=properties)

    def update_environment_configuration(
        self,
        data_product_id: UUID,
        id: UUID,
        request: UpdateToolEnvironmentConfigurationRequest,
    ) -> ToolEnvironmentConfiguration:
        tool = ensure_tool_exists(id, self.db, data_product_id)
        tool_type = plugin_registry.tool_type(tool.platform_key, tool.tool_type)
        environment_ids = {
            declaration.environment_id
            for declaration in self._data_product(data_product_id).environments
        }
        for environment_id in request.overrides:
            self._ensure_runs_in(environment_id, environment_ids)
        tool.base_values = {
            **tool.base_values,
            **self._validated(tool_type, request.base_values),
        }
        tool.overrides = [
            ToolEnvironmentOverride(
                environment_id=environment_id,
                values=self._validated(tool_type, values),
            )
            for environment_id, values in request.overrides.items()
            if values
        ]
        self.db.flush()
        return self.get_environment_configuration(data_product_id, id)

    def apply_environment_configuration(
        self, data_product_id: UUID, id: UUID, environment_id: UUID
    ) -> None:
        environments = {
            declaration.environment_id: declaration.environment
            for declaration in self._data_product(data_product_id).environments
        }
        self._ensure_runs_in(environment_id, set(environments))
        environment = environments[environment_id]
        configuration = self.get_environment_configuration(data_product_id, id)
        context.queue_event(
            ToolEnvironmentConfigurationAppliedEvent(
                id=id,
                data_product_id=data_product_id,
                environment=environment.acronym,
                configuration={
                    prop.name: next(
                        value.effective_value
                        for value in prop.environments
                        if value.id == environment_id
                    )
                    for prop in configuration.properties
                },
            )
        )

    def _data_product(self, data_product_id: UUID) -> DataProductModel:
        return ensure_data_product_exists(
            data_product_id,
            self.db,
            options=[selectinload(DataProductModel.environments)],
        )

    @staticmethod
    def _ensure_runs_in(environment_id: UUID, environment_ids: set[UUID]) -> None:
        if environment_id not in environment_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Data Product does not run in environment {environment_id}",
            )

    @staticmethod
    def _validated(tool_type: ToolType, values: dict[str, str]) -> dict[str, str]:
        properties = {p.name: p for p in tool_type.overridable_properties}
        for name, value in values.items():
            if name not in properties:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{name}' is not an overridable property of {tool_type.display_name}",
                )
            if value not in properties[name].allowed_values:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"'{value}' is not an allowed value for {properties[name].label}. "
                        f"Allowed values: {', '.join(properties[name].allowed_values)}"
                    ),
                )
        return values
