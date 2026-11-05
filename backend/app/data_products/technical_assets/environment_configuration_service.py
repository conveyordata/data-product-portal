from typing import Any, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import (
    ENVIRONMENT_DISPLAY_ORDER,
)
from app.configuration.environments.model import Environment as EnvironmentModel
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import DataProductEnvironment
from app.data_products.technical_assets.enums import TechnicalMapping
from app.data_products.technical_assets.model import (
    TechnicalAsset as TechnicalAssetModel,
)
from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import (
    EnvironmentConfigurationError,
    EnvironmentFieldError,
    PluginContext,
    TechnicalAssetPlugin,
)

type EnvironmentValues = dict[UUID, dict[str, Any]]


class TechnicalAssetEnvironmentConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_values(self, technical_asset: TechnicalAssetModel) -> EnvironmentValues:
        plugin = plugin_registry.get(technical_asset.configuration.configuration_type)
        if plugin.environment_configuration is None:
            return {}
        _, stored = self._load(plugin, technical_asset.configuration_id)
        values: EnvironmentValues = {}
        for declaration in technical_asset.owner.environments:
            environment = declaration.environment
            if environment.id not in stored:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Technical asset {technical_asset.id} has no {plugin.name} environment configuration for environment {environment.name} ({environment.id})",
                )
            values[environment.id] = stored[environment.id]
        return values

    def prepare_create(
        self,
        configuration: TechnicalAssetPlugin,
        context: PluginContext,
        provided: EnvironmentValues,
    ) -> EnvironmentValues:
        plugin = type(configuration)
        if plugin.environment_configuration is None:
            if provided:
                raise self._no_environment_configuration()
            return {}
        environments = self._environments(context.data_product.id)
        submitted = {
            **provided,
            **{
                environment.id: {
                    **self._defaults(plugin, environment, configuration.model_dump()),
                    **provided.get(environment.id, {}),
                }
                for environment in environments
            },
        }
        return self._validated(
            configuration, context, environments, submitted, stored={}
        )

    def create(
        self,
        configuration_id: UUID,
        plugin: type[TechnicalAssetPlugin],
        values: EnvironmentValues,
    ) -> None:
        for environment_id, environment_values in values.items():
            self._add_row(plugin, configuration_id, environment_id, environment_values)
        self.db.flush()

    def validate(
        self, technical_asset: TechnicalAssetModel, submitted: EnvironmentValues
    ) -> None:
        self._validated_submission(technical_asset, submitted)

    def replace(
        self, technical_asset: TechnicalAssetModel, submitted: EnvironmentValues
    ) -> None:
        plugin, rows, values = self._validated_submission(technical_asset, submitted)
        for environment_id, environment_values in values.items():
            if (row := rows.get(environment_id)) is None:
                self._add_row(
                    plugin,
                    technical_asset.configuration_id,
                    environment_id,
                    environment_values,
                )
            else:
                for field, value in environment_values.items():
                    setattr(row, field, value)
        self.db.flush()

    def add_environments(
        self,
        data_product: DataProductModel,
        environments: Sequence[EnvironmentModel],
    ) -> None:
        if not environments:
            return
        technical_assets = self.db.scalars(
            select(TechnicalAssetModel).where(
                TechnicalAssetModel.owner_id == data_product.id
            )
        ).all()
        for technical_asset in technical_assets:
            plugin = plugin_registry.get(
                technical_asset.configuration.configuration_type
            )
            if plugin.environment_configuration is None:
                continue
            configuration = plugin.model_validate(technical_asset.configuration)
            shared = configuration.model_dump()
            added = {
                environment.id: self._valid_defaults(plugin, environment, shared)
                for environment in environments
            }
            _, stored = self._load(plugin, technical_asset.configuration_id)
            try:
                configuration.validate_environment_configuration(
                    {**stored, **added}, self._context(technical_asset), self.db
                )
            except EnvironmentConfigurationError as error:
                raise self._http_error(error.errors)
            for environment_id, values in added.items():
                self._add_row(
                    plugin, technical_asset.configuration_id, environment_id, values
                )
        self.db.flush()

    @staticmethod
    def _context(technical_asset: TechnicalAssetModel) -> PluginContext:
        return PluginContext.build(
            technical_asset.owner,
            technical_asset.namespace,
            TechnicalMapping(technical_asset.technical_mapping),
            technical_asset.id,
        )

    def _validated_submission(
        self, technical_asset: TechnicalAssetModel, submitted: EnvironmentValues
    ) -> tuple[type[TechnicalAssetPlugin], dict[UUID, Any], EnvironmentValues]:
        plugin = plugin_registry.get(technical_asset.configuration.configuration_type)
        if plugin.environment_configuration is None:
            raise self._no_environment_configuration()
        rows, stored = self._load(plugin, technical_asset.configuration_id)
        values = self._validated(
            plugin.model_validate(technical_asset.configuration),
            self._context(technical_asset),
            [
                declaration.environment
                for declaration in technical_asset.owner.environments
            ],
            submitted,
            stored,
        )
        return plugin, rows, values

    def _validated(
        self,
        configuration: TechnicalAssetPlugin,
        context: PluginContext,
        environments: Sequence[EnvironmentModel],
        submitted: EnvironmentValues,
        stored: EnvironmentValues,
    ) -> EnvironmentValues:
        plugin = type(configuration)
        self._check_environments(environments, submitted)
        values: EnvironmentValues = {}
        errors: list[EnvironmentFieldError] = []
        for environment in environments:
            parsed, parse_errors = self._parse(
                plugin,
                environment,
                submitted[environment.id],
                stored.get(environment.id, {}),
            )
            errors.extend(parse_errors)
            if parsed is not None:
                values[environment.id] = parsed
        if errors:
            raise self._http_error(errors)
        try:
            configuration.validate_environment_configuration(values, context, self.db)
        except EnvironmentConfigurationError as error:
            raise self._http_error(error.errors)
        return values

    def _check_environments(
        self, environments: Sequence[EnvironmentModel], submitted: EnvironmentValues
    ) -> None:
        expected = {environment.id for environment in environments}
        errors = [
            EnvironmentFieldError(environment_id=environment_id, message=message)
            for environment_ids, message in [
                (submitted.keys() - expected, "Unknown environment"),
                (expected - submitted.keys(), "Missing environment"),
            ]
            for environment_id in environment_ids
        ]
        if errors:
            raise self._http_error(errors)

    def _parse(
        self,
        plugin: type[TechnicalAssetPlugin],
        environment: EnvironmentModel,
        raw: dict[str, Any],
        stored: dict[str, Any],
    ) -> tuple[Optional[dict[str, Any]], list[EnvironmentFieldError]]:
        schema: Any = plugin.environment_configuration
        try:
            parsed = schema.model_validate(raw).model_dump(mode="json")
        except ValidationError as error:
            return None, [
                EnvironmentFieldError(
                    environment_id=environment.id,
                    field=str(item["loc"][0]) if item["loc"] else None,
                    message=str(item["ctx"]["error"])
                    if item["type"] == "value_error"
                    else item["msg"],
                )
                for item in error.errors()
            ]
        return parsed, self._option_errors(plugin, environment, parsed, stored)

    def _valid_defaults(
        self,
        plugin: type[TechnicalAssetPlugin],
        environment: EnvironmentModel,
        shared: dict[str, Any],
    ) -> dict[str, Any]:
        parsed, errors = self._parse(
            plugin, environment, self._defaults(plugin, environment, shared), {}
        )
        if errors:
            raise self._http_error(
                [
                    error.model_copy(
                        update={
                            "message": f"Default of plugin {plugin.name} for environment {environment.name} is invalid: {error.message}"
                        }
                    )
                    for error in errors
                ]
            )
        return parsed  # type: ignore[return-value]

    def _option_errors(
        self,
        plugin: type[TechnicalAssetPlugin],
        environment: EnvironmentModel,
        parsed: dict[str, Any],
        stored: dict[str, Any],
    ) -> list[EnvironmentFieldError]:
        schema: Any = plugin.environment_configuration
        return [
            EnvironmentFieldError(
                environment_id=environment.id,
                field=field,
                message="Option is not allowed in this environment",
            )
            for field, options in schema.allowed_options(environment).items()
            if parsed[field] not in options
            and (field not in stored or stored[field] != parsed[field])
        ]

    def _defaults(
        self,
        plugin: type[TechnicalAssetPlugin],
        environment: EnvironmentModel,
        shared: dict[str, Any],
    ) -> dict[str, Any]:
        schema: Any = plugin.environment_configuration
        return {
            field: self._render(plugin, environment, field, value, shared)
            for field, value in schema.defaults(environment).items()
        }

    def _render(
        self,
        plugin: type[TechnicalAssetPlugin],
        environment: EnvironmentModel,
        field: str,
        value: Any,
        shared: dict[str, Any],
    ) -> Any:
        if not isinstance(value, str):
            return value
        try:
            return value.format(**shared)
        except (KeyError, IndexError, ValueError) as error:
            raise self._http_error(
                [
                    EnvironmentFieldError(
                        environment_id=environment.id,
                        field=field,
                        message=f"Default of plugin {plugin.name} for environment {environment.name} is invalid: cannot render {value!r} ({error!r})",
                    )
                ]
            )

    def _add_row(
        self,
        plugin: type[TechnicalAssetPlugin],
        configuration_id: UUID,
        environment_id: UUID,
        values: dict[str, Any],
    ) -> None:
        schema: Any = plugin.environment_configuration
        self.db.add(
            schema.Meta.orm_model(
                configuration_id=configuration_id,
                environment_id=environment_id,
                **values,
            )
        )

    def _load(
        self, plugin: type[TechnicalAssetPlugin], configuration_id: UUID
    ) -> tuple[dict[UUID, Any], EnvironmentValues]:
        schema: Any = plugin.environment_configuration
        orm_model = schema.Meta.orm_model
        rows = {
            row.environment_id: row
            for row in self.db.scalars(
                select(orm_model).where(orm_model.configuration_id == configuration_id)
            )
        }
        return rows, {
            environment_id: schema.model_validate(row).model_dump(mode="json")
            for environment_id, row in rows.items()
        }

    def _environments(self, data_product_id: UUID) -> list[EnvironmentModel]:
        return list(
            self.db.scalars(
                select(EnvironmentModel)
                .join(
                    DataProductEnvironment,
                    DataProductEnvironment.environment_id == EnvironmentModel.id,
                )
                .where(DataProductEnvironment.data_product_id == data_product_id)
                .order_by(*ENVIRONMENT_DISPLAY_ORDER)
            )
        )

    @staticmethod
    def _no_environment_configuration() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This technical asset has no per-environment configuration",
        )

    @staticmethod
    def _http_error(errors: list[EnvironmentFieldError]) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[error.model_dump(mode="json") for error in errors],
        )
