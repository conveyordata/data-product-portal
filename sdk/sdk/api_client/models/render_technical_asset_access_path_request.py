from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.azure_blob_technical_asset_configuration import (
        AzureBlobTechnicalAssetConfiguration,
    )
    from ..models.databricks_technical_asset_configuration import (
        DatabricksTechnicalAssetConfiguration,
    )
    from ..models.glue_technical_asset_configuration import (
        GlueTechnicalAssetConfiguration,
    )
    from ..models.osi_semantic_model_technical_asset_configuration import (
        OSISemanticModelTechnicalAssetConfiguration,
    )
    from ..models.postgre_sql_technical_asset_configuration import (
        PostgreSQLTechnicalAssetConfiguration,
    )
    from ..models.redshift_technical_asset_configuration import (
        RedshiftTechnicalAssetConfiguration,
    )
    from ..models.render_technical_asset_access_path_request_values_type_0 import (
        RenderTechnicalAssetAccessPathRequestValuesType0,
    )
    from ..models.rust_fs_technical_asset_configuration import (
        RustFSTechnicalAssetConfiguration,
    )
    from ..models.s3_technical_asset_configuration import S3TechnicalAssetConfiguration
    from ..models.snowflake_technical_asset_configuration import (
        SnowflakeTechnicalAssetConfiguration,
    )


T = TypeVar("T", bound="RenderTechnicalAssetAccessPathRequest")


@_attrs_define
class RenderTechnicalAssetAccessPathRequest:
    """
    Attributes:
        platform_id (None | Unset | UUID):
        service_id (None | Unset | UUID):
        configuration (AzureBlobTechnicalAssetConfiguration | DatabricksTechnicalAssetConfiguration |
            GlueTechnicalAssetConfiguration | None | OSISemanticModelTechnicalAssetConfiguration |
            PostgreSQLTechnicalAssetConfiguration | RedshiftTechnicalAssetConfiguration | RustFSTechnicalAssetConfiguration
            | S3TechnicalAssetConfiguration | SnowflakeTechnicalAssetConfiguration | Unset):
        plugin_key (None | str | Unset):
        values (None | RenderTechnicalAssetAccessPathRequestValuesType0 | Unset):
    """

    platform_id: None | Unset | UUID = UNSET
    service_id: None | Unset | UUID = UNSET
    configuration: (
        AzureBlobTechnicalAssetConfiguration
        | DatabricksTechnicalAssetConfiguration
        | GlueTechnicalAssetConfiguration
        | None
        | OSISemanticModelTechnicalAssetConfiguration
        | PostgreSQLTechnicalAssetConfiguration
        | RedshiftTechnicalAssetConfiguration
        | RustFSTechnicalAssetConfiguration
        | S3TechnicalAssetConfiguration
        | SnowflakeTechnicalAssetConfiguration
        | Unset
    ) = UNSET
    plugin_key: None | str | Unset = UNSET
    values: None | RenderTechnicalAssetAccessPathRequestValuesType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.azure_blob_technical_asset_configuration import (
            AzureBlobTechnicalAssetConfiguration,
        )
        from ..models.databricks_technical_asset_configuration import (
            DatabricksTechnicalAssetConfiguration,
        )
        from ..models.glue_technical_asset_configuration import (
            GlueTechnicalAssetConfiguration,
        )
        from ..models.osi_semantic_model_technical_asset_configuration import (
            OSISemanticModelTechnicalAssetConfiguration,
        )
        from ..models.postgre_sql_technical_asset_configuration import (
            PostgreSQLTechnicalAssetConfiguration,
        )
        from ..models.redshift_technical_asset_configuration import (
            RedshiftTechnicalAssetConfiguration,
        )
        from ..models.render_technical_asset_access_path_request_values_type_0 import (
            RenderTechnicalAssetAccessPathRequestValuesType0,
        )
        from ..models.rust_fs_technical_asset_configuration import (
            RustFSTechnicalAssetConfiguration,
        )
        from ..models.s3_technical_asset_configuration import (
            S3TechnicalAssetConfiguration,
        )
        from ..models.snowflake_technical_asset_configuration import (
            SnowflakeTechnicalAssetConfiguration,
        )

        platform_id: None | str | Unset
        if isinstance(self.platform_id, Unset):
            platform_id = UNSET
        elif isinstance(self.platform_id, UUID):
            platform_id = str(self.platform_id)
        else:
            platform_id = self.platform_id

        service_id: None | str | Unset
        if isinstance(self.service_id, Unset):
            service_id = UNSET
        elif isinstance(self.service_id, UUID):
            service_id = str(self.service_id)
        else:
            service_id = self.service_id

        configuration: dict[str, Any] | None | Unset
        if isinstance(self.configuration, Unset):
            configuration = UNSET
        elif isinstance(self.configuration, S3TechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, RustFSTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, GlueTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, DatabricksTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, SnowflakeTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, RedshiftTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, PostgreSQLTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        elif isinstance(
            self.configuration, OSISemanticModelTechnicalAssetConfiguration
        ):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, AzureBlobTechnicalAssetConfiguration):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration

        plugin_key: None | str | Unset
        if isinstance(self.plugin_key, Unset):
            plugin_key = UNSET
        else:
            plugin_key = self.plugin_key

        values: dict[str, Any] | None | Unset
        if isinstance(self.values, Unset):
            values = UNSET
        elif isinstance(self.values, RenderTechnicalAssetAccessPathRequestValuesType0):
            values = self.values.to_dict()
        else:
            values = self.values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if platform_id is not UNSET:
            field_dict["platform_id"] = platform_id
        if service_id is not UNSET:
            field_dict["service_id"] = service_id
        if configuration is not UNSET:
            field_dict["configuration"] = configuration
        if plugin_key is not UNSET:
            field_dict["plugin_key"] = plugin_key
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.azure_blob_technical_asset_configuration import (
            AzureBlobTechnicalAssetConfiguration,
        )
        from ..models.databricks_technical_asset_configuration import (
            DatabricksTechnicalAssetConfiguration,
        )
        from ..models.glue_technical_asset_configuration import (
            GlueTechnicalAssetConfiguration,
        )
        from ..models.osi_semantic_model_technical_asset_configuration import (
            OSISemanticModelTechnicalAssetConfiguration,
        )
        from ..models.postgre_sql_technical_asset_configuration import (
            PostgreSQLTechnicalAssetConfiguration,
        )
        from ..models.redshift_technical_asset_configuration import (
            RedshiftTechnicalAssetConfiguration,
        )
        from ..models.render_technical_asset_access_path_request_values_type_0 import (
            RenderTechnicalAssetAccessPathRequestValuesType0,
        )
        from ..models.rust_fs_technical_asset_configuration import (
            RustFSTechnicalAssetConfiguration,
        )
        from ..models.s3_technical_asset_configuration import (
            S3TechnicalAssetConfiguration,
        )
        from ..models.snowflake_technical_asset_configuration import (
            SnowflakeTechnicalAssetConfiguration,
        )

        d = dict(src_dict)

        def _parse_platform_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                platform_id_type_0 = UUID(data)

                return platform_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        platform_id = _parse_platform_id(d.pop("platform_id", UNSET))

        def _parse_service_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_id_type_0 = UUID(data)

                return service_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        service_id = _parse_service_id(d.pop("service_id", UNSET))

        def _parse_configuration(
            data: object,
        ) -> (
            AzureBlobTechnicalAssetConfiguration
            | DatabricksTechnicalAssetConfiguration
            | GlueTechnicalAssetConfiguration
            | None
            | OSISemanticModelTechnicalAssetConfiguration
            | PostgreSQLTechnicalAssetConfiguration
            | RedshiftTechnicalAssetConfiguration
            | RustFSTechnicalAssetConfiguration
            | S3TechnicalAssetConfiguration
            | SnowflakeTechnicalAssetConfiguration
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_0 = S3TechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_0_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_1 = (
                    RustFSTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_2 = GlueTechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_0_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_3 = (
                    DatabricksTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_4 = (
                    SnowflakeTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_5 = (
                    RedshiftTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_6 = (
                    PostgreSQLTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_7 = (
                    OSISemanticModelTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0_type_8 = (
                    AzureBlobTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_0_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                AzureBlobTechnicalAssetConfiguration
                | DatabricksTechnicalAssetConfiguration
                | GlueTechnicalAssetConfiguration
                | None
                | OSISemanticModelTechnicalAssetConfiguration
                | PostgreSQLTechnicalAssetConfiguration
                | RedshiftTechnicalAssetConfiguration
                | RustFSTechnicalAssetConfiguration
                | S3TechnicalAssetConfiguration
                | SnowflakeTechnicalAssetConfiguration
                | Unset,
                data,
            )

        configuration = _parse_configuration(d.pop("configuration", UNSET))

        def _parse_plugin_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plugin_key = _parse_plugin_key(d.pop("plugin_key", UNSET))

        def _parse_values(
            data: object,
        ) -> None | RenderTechnicalAssetAccessPathRequestValuesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                values_type_0 = (
                    RenderTechnicalAssetAccessPathRequestValuesType0.from_dict(data)
                )

                return values_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | RenderTechnicalAssetAccessPathRequestValuesType0 | Unset, data
            )

        values = _parse_values(d.pop("values", UNSET))

        render_technical_asset_access_path_request = cls(
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
            plugin_key=plugin_key,
            values=values,
        )

        render_technical_asset_access_path_request.additional_properties = d
        return render_technical_asset_access_path_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
