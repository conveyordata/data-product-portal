from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_asset_status import TechnicalAssetStatus
from ..models.technical_mapping import TechnicalMapping

if TYPE_CHECKING:
    from ..models.data_product import DataProduct
    from ..models.databricks_technical_asset_configuration import (
        DatabricksTechnicalAssetConfiguration,
    )
    from ..models.glue_technical_asset_configuration import (
        GlueTechnicalAssetConfiguration,
    )
    from ..models.osi_semantic_model_technical_asset_configuration import (
        OSISemanticModelTechnicalAssetConfiguration,
    )
    from ..models.output_port_link import OutputPortLink
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
    from ..models.tag import Tag
    from ..models.technical_info import TechnicalInfo


T = TypeVar("T", bound="GetTechnicalAssetsResponseItem")


@_attrs_define
class GetTechnicalAssetsResponseItem:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        namespace (str):
        owner_id (UUID):
        platform_id (UUID):
        service_id (UUID):
        status (TechnicalAssetStatus):
        technical_mapping (TechnicalMapping):
        configuration (DatabricksTechnicalAssetConfiguration | GlueTechnicalAssetConfiguration |
            OSISemanticModelTechnicalAssetConfiguration | PostgreSQLTechnicalAssetConfiguration |
            RedshiftTechnicalAssetConfiguration | S3TechnicalAssetConfiguration | SnowflakeTechnicalAssetConfiguration):
        owner (DataProduct):
        output_port_links (list[OutputPortLink]):
        tags (list[Tag]):
        source_aligned (bool): DEPRECATED: Use 'technical_mapping' instead. This field will be removed in a future
            version.
        result_string (str):
        technical_info (list[TechnicalInfo]):
    """

    id: UUID
    name: str
    description: str
    namespace: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: TechnicalAssetStatus
    technical_mapping: TechnicalMapping
    configuration: (
        DatabricksTechnicalAssetConfiguration
        | GlueTechnicalAssetConfiguration
        | OSISemanticModelTechnicalAssetConfiguration
        | PostgreSQLTechnicalAssetConfiguration
        | RedshiftTechnicalAssetConfiguration
        | S3TechnicalAssetConfiguration
        | SnowflakeTechnicalAssetConfiguration
    )
    owner: DataProduct
    output_port_links: list[OutputPortLink]
    tags: list[Tag]
    source_aligned: bool
    result_string: str
    technical_info: list[TechnicalInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.databricks_technical_asset_configuration import (
            DatabricksTechnicalAssetConfiguration,
        )
        from ..models.glue_technical_asset_configuration import (
            GlueTechnicalAssetConfiguration,
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

        description = self.description

        namespace = self.namespace

        owner_id = str(self.owner_id)

        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        status = self.status.value

        technical_mapping = self.technical_mapping.value

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
        else:
            configuration = self.configuration.to_dict()

        owner = self.owner.to_dict()

        output_port_links = []
        for output_port_links_item_data in self.output_port_links:
            output_port_links_item = output_port_links_item_data.to_dict()
            output_port_links.append(output_port_links_item)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        source_aligned = self.source_aligned

        result_string = self.result_string

        technical_info = []
        for technical_info_item_data in self.technical_info:
            technical_info_item = technical_info_item_data.to_dict()
            technical_info.append(technical_info_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "namespace": namespace,
                "owner_id": owner_id,
                "platform_id": platform_id,
                "service_id": service_id,
                "status": status,
                "technical_mapping": technical_mapping,
                "configuration": configuration,
                "owner": owner,
                "output_port_links": output_port_links,
                "tags": tags,
                "sourceAligned": source_aligned,
                "result_string": result_string,
                "technical_info": technical_info,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product import DataProduct
        from ..models.databricks_technical_asset_configuration import (
            DatabricksTechnicalAssetConfiguration,
        )
        from ..models.glue_technical_asset_configuration import (
            GlueTechnicalAssetConfiguration,
        )
        from ..models.osi_semantic_model_technical_asset_configuration import (
            OSISemanticModelTechnicalAssetConfiguration,
        )
        from ..models.output_port_link import OutputPortLink
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
        from ..models.tag import Tag
        from ..models.technical_info import TechnicalInfo

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        owner_id = UUID(d.pop("owner_id"))

        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

        status = TechnicalAssetStatus(d.pop("status"))

        technical_mapping = TechnicalMapping(d.pop("technical_mapping"))

        def _parse_configuration(
            data: object,
        ) -> (
            DatabricksTechnicalAssetConfiguration
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
            if not isinstance(data, dict):
                raise TypeError()
            configuration_type_6 = (
                OSISemanticModelTechnicalAssetConfiguration.from_dict(data)
            )

            return configuration_type_6

        configuration = _parse_configuration(d.pop("configuration"))

        owner = DataProduct.from_dict(d.pop("owner"))

        output_port_links = []
        _output_port_links = d.pop("output_port_links")
        for output_port_links_item_data in _output_port_links:
            output_port_links_item = OutputPortLink.from_dict(
                output_port_links_item_data
            )

            output_port_links.append(output_port_links_item)

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        source_aligned = d.pop("sourceAligned")

        result_string = d.pop("result_string")

        technical_info = []
        _technical_info = d.pop("technical_info")
        for technical_info_item_data in _technical_info:
            technical_info_item = TechnicalInfo.from_dict(technical_info_item_data)

            technical_info.append(technical_info_item)

        get_technical_assets_response_item = cls(
            id=id,
            name=name,
            description=description,
            namespace=namespace,
            owner_id=owner_id,
            platform_id=platform_id,
            service_id=service_id,
            status=status,
            technical_mapping=technical_mapping,
            configuration=configuration,
            owner=owner,
            output_port_links=output_port_links,
            tags=tags,
            source_aligned=source_aligned,
            result_string=result_string,
            technical_info=technical_info,
        )

        get_technical_assets_response_item.additional_properties = d
        return get_technical_assets_response_item

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
