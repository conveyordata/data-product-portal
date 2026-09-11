from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_mapping import TechnicalMapping
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.azure_blob_technical_asset_configuration import (
        AzureBlobTechnicalAssetConfiguration,
    )
    from ..models.create_technical_asset_request_values_type_0 import (
        CreateTechnicalAssetRequestValuesType0,
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
    from ..models.rust_fs_technical_asset_configuration import (
        RustFSTechnicalAssetConfiguration,
    )
    from ..models.s3_technical_asset_configuration import S3TechnicalAssetConfiguration
    from ..models.snowflake_technical_asset_configuration import (
        SnowflakeTechnicalAssetConfiguration,
    )


T = TypeVar("T", bound="CreateTechnicalAssetRequest")


@_attrs_define
class CreateTechnicalAssetRequest:
    """
    Attributes:
        name (str):
        description (str):
        namespace (str):
        tag_ids (list[UUID]):
        platform_id (None | Unset | UUID):
        service_id (None | Unset | UUID):
        configuration (AzureBlobTechnicalAssetConfiguration | DatabricksTechnicalAssetConfiguration |
            GlueTechnicalAssetConfiguration | None | OSISemanticModelTechnicalAssetConfiguration |
            PostgreSQLTechnicalAssetConfiguration | RedshiftTechnicalAssetConfiguration | RustFSTechnicalAssetConfiguration
            | S3TechnicalAssetConfiguration | SnowflakeTechnicalAssetConfiguration | Unset):
        plugin_key (None | str | Unset):
        values (CreateTechnicalAssetRequestValuesType0 | None | Unset):
        source_aligned (bool | None | Unset): DEPRECATED: Use 'technical_mapping' instead. This field will be removed in
            a future version.
        technical_mapping (None | TechnicalMapping | Unset):
        access_mode_ids (list[UUID] | Unset):
    """

    name: str
    description: str
    namespace: str
    tag_ids: list[UUID]
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
    values: CreateTechnicalAssetRequestValuesType0 | None | Unset = UNSET
    source_aligned: bool | None | Unset = UNSET
    technical_mapping: None | TechnicalMapping | Unset = UNSET
    access_mode_ids: list[UUID] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.azure_blob_technical_asset_configuration import (
            AzureBlobTechnicalAssetConfiguration,
        )
        from ..models.create_technical_asset_request_values_type_0 import (
            CreateTechnicalAssetRequestValuesType0,
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
        from ..models.rust_fs_technical_asset_configuration import (
            RustFSTechnicalAssetConfiguration,
        )
        from ..models.s3_technical_asset_configuration import (
            S3TechnicalAssetConfiguration,
        )
        from ..models.snowflake_technical_asset_configuration import (
            SnowflakeTechnicalAssetConfiguration,
        )

        name = self.name

        description = self.description

        namespace = self.namespace

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

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
        elif isinstance(self.values, CreateTechnicalAssetRequestValuesType0):
            values = self.values.to_dict()
        else:
            values = self.values

        source_aligned: bool | None | Unset
        if isinstance(self.source_aligned, Unset):
            source_aligned = UNSET
        else:
            source_aligned = self.source_aligned

        technical_mapping: None | str | Unset
        if isinstance(self.technical_mapping, Unset):
            technical_mapping = UNSET
        elif isinstance(self.technical_mapping, TechnicalMapping):
            technical_mapping = self.technical_mapping.value
        else:
            technical_mapping = self.technical_mapping

        access_mode_ids: list[str] | Unset = UNSET
        if not isinstance(self.access_mode_ids, Unset):
            access_mode_ids = []
            for access_mode_ids_item_data in self.access_mode_ids:
                access_mode_ids_item = str(access_mode_ids_item_data)
                access_mode_ids.append(access_mode_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "namespace": namespace,
                "tag_ids": tag_ids,
            }
        )
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
        if source_aligned is not UNSET:
            field_dict["sourceAligned"] = source_aligned
        if technical_mapping is not UNSET:
            field_dict["technical_mapping"] = technical_mapping
        if access_mode_ids is not UNSET:
            field_dict["access_mode_ids"] = access_mode_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.azure_blob_technical_asset_configuration import (
            AzureBlobTechnicalAssetConfiguration,
        )
        from ..models.create_technical_asset_request_values_type_0 import (
            CreateTechnicalAssetRequestValuesType0,
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
        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

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
        ) -> CreateTechnicalAssetRequestValuesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                values_type_0 = CreateTechnicalAssetRequestValuesType0.from_dict(data)

                return values_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreateTechnicalAssetRequestValuesType0 | None | Unset, data)

        values = _parse_values(d.pop("values", UNSET))

        def _parse_source_aligned(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        source_aligned = _parse_source_aligned(d.pop("sourceAligned", UNSET))

        def _parse_technical_mapping(data: object) -> None | TechnicalMapping | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                technical_mapping_type_0 = TechnicalMapping(data)

                return technical_mapping_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TechnicalMapping | Unset, data)

        technical_mapping = _parse_technical_mapping(d.pop("technical_mapping", UNSET))

        _access_mode_ids = d.pop("access_mode_ids", UNSET)
        access_mode_ids: list[UUID] | Unset = UNSET
        if _access_mode_ids is not UNSET:
            access_mode_ids = []
            for access_mode_ids_item_data in _access_mode_ids:
                access_mode_ids_item = UUID(access_mode_ids_item_data)

                access_mode_ids.append(access_mode_ids_item)

        create_technical_asset_request = cls(
            name=name,
            description=description,
            namespace=namespace,
            tag_ids=tag_ids,
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
            plugin_key=plugin_key,
            values=values,
            source_aligned=source_aligned,
            technical_mapping=technical_mapping,
            access_mode_ids=access_mode_ids,
        )

        create_technical_asset_request.additional_properties = d
        return create_technical_asset_request

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
