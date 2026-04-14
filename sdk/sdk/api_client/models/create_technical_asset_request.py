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
        platform_id (UUID):
        service_id (UUID):
        configuration (AzureBlobTechnicalAssetConfiguration | DatabricksTechnicalAssetConfiguration |
            GlueTechnicalAssetConfiguration | OSISemanticModelTechnicalAssetConfiguration |
            PostgreSQLTechnicalAssetConfiguration | RedshiftTechnicalAssetConfiguration | S3TechnicalAssetConfiguration |
            SnowflakeTechnicalAssetConfiguration):
        tag_ids (list[UUID]):
        source_aligned (bool | None | Unset): DEPRECATED: Use 'technical_mapping' instead. This field will be removed in
            a future version.
        technical_mapping (None | TechnicalMapping | Unset):
    """

    name: str
    description: str
    namespace: str
    platform_id: UUID
    service_id: UUID
    configuration: (
        AzureBlobTechnicalAssetConfiguration
        | DatabricksTechnicalAssetConfiguration
        | GlueTechnicalAssetConfiguration
        | OSISemanticModelTechnicalAssetConfiguration
        | PostgreSQLTechnicalAssetConfiguration
        | RedshiftTechnicalAssetConfiguration
        | S3TechnicalAssetConfiguration
        | SnowflakeTechnicalAssetConfiguration
    )
    tag_ids: list[UUID]
    source_aligned: bool | None | Unset = UNSET
    technical_mapping: None | TechnicalMapping | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
        from ..models.s3_technical_asset_configuration import (
            S3TechnicalAssetConfiguration,
        )
        from ..models.snowflake_technical_asset_configuration import (
            SnowflakeTechnicalAssetConfiguration,
        )

        name = self.name

        description = self.description

        namespace = self.namespace

        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        configuration: dict[str, Any]
        if isinstance(self.configuration, S3TechnicalAssetConfiguration):
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
        else:
            configuration = self.configuration.to_dict()

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "namespace": namespace,
                "platform_id": platform_id,
                "service_id": service_id,
                "configuration": configuration,
                "tag_ids": tag_ids,
            }
        )
        if source_aligned is not UNSET:
            field_dict["sourceAligned"] = source_aligned
        if technical_mapping is not UNSET:
            field_dict["technical_mapping"] = technical_mapping

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

        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

        def _parse_configuration(
            data: object,
        ) -> (
            AzureBlobTechnicalAssetConfiguration
            | DatabricksTechnicalAssetConfiguration
            | GlueTechnicalAssetConfiguration
            | OSISemanticModelTechnicalAssetConfiguration
            | PostgreSQLTechnicalAssetConfiguration
            | RedshiftTechnicalAssetConfiguration
            | S3TechnicalAssetConfiguration
            | SnowflakeTechnicalAssetConfiguration
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0 = S3TechnicalAssetConfiguration.from_dict(data)

                return configuration_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_1 = GlueTechnicalAssetConfiguration.from_dict(data)

                return configuration_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_2 = DatabricksTechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_3 = SnowflakeTechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_4 = RedshiftTechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_5 = PostgreSQLTechnicalAssetConfiguration.from_dict(
                    data
                )

                return configuration_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_6 = (
                    OSISemanticModelTechnicalAssetConfiguration.from_dict(data)
                )

                return configuration_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            configuration_type_7 = AzureBlobTechnicalAssetConfiguration.from_dict(data)

            return configuration_type_7

        configuration = _parse_configuration(d.pop("configuration"))

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

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

        create_technical_asset_request = cls(
            name=name,
            description=description,
            namespace=namespace,
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
            tag_ids=tag_ids,
            source_aligned=source_aligned,
            technical_mapping=technical_mapping,
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
