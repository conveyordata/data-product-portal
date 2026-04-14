from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_asset_status import TechnicalAssetStatus
from ..models.technical_mapping import TechnicalMapping

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


T = TypeVar("T", bound="TechnicalAsset")


@_attrs_define
class TechnicalAsset:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        status (TechnicalAssetStatus):
        technical_mapping (TechnicalMapping):
        owner_id (UUID):
        platform_id (UUID):
        service_id (UUID):
        configuration (AzureBlobTechnicalAssetConfiguration | DatabricksTechnicalAssetConfiguration |
            GlueTechnicalAssetConfiguration | OSISemanticModelTechnicalAssetConfiguration |
            PostgreSQLTechnicalAssetConfiguration | RedshiftTechnicalAssetConfiguration | S3TechnicalAssetConfiguration |
            SnowflakeTechnicalAssetConfiguration):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    owner_id: UUID
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

        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        status = self.status.value

        technical_mapping = self.technical_mapping.value

        owner_id = str(self.owner_id)

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "status": status,
                "technical_mapping": technical_mapping,
                "owner_id": owner_id,
                "platform_id": platform_id,
                "service_id": service_id,
                "configuration": configuration,
            }
        )

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
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        status = TechnicalAssetStatus(d.pop("status"))

        technical_mapping = TechnicalMapping(d.pop("technical_mapping"))

        owner_id = UUID(d.pop("owner_id"))

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

        technical_asset = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            technical_mapping=technical_mapping,
            owner_id=owner_id,
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
        )

        technical_asset.additional_properties = d
        return technical_asset

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
