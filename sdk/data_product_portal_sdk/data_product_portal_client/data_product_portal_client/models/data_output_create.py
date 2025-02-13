from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_output_status import DataOutputStatus

if TYPE_CHECKING:
    from ..models.databricks_data_output import DatabricksDataOutput
    from ..models.glue_data_output import GlueDataOutput
    from ..models.s3_data_output import S3DataOutput
    from ..models.snowflake_data_output import SnowflakeDataOutput


T = TypeVar("T", bound="DataOutputCreate")


@_attrs_define
class DataOutputCreate:
    """
    Attributes:
        name (str):
        description (str):
        external_id (str):
        owner_id (UUID):
        platform_id (UUID):
        service_id (UUID):
        status (DataOutputStatus):
        configuration (Union['DatabricksDataOutput', 'GlueDataOutput', 'S3DataOutput', 'SnowflakeDataOutput']):
        source_aligned (bool):
        tag_ids (list[UUID]):
    """

    name: str
    description: str
    external_id: str
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    status: DataOutputStatus
    configuration: Union[
        "DatabricksDataOutput", "GlueDataOutput", "S3DataOutput", "SnowflakeDataOutput"
    ]
    source_aligned: bool
    tag_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.databricks_data_output import DatabricksDataOutput
        from ..models.glue_data_output import GlueDataOutput
        from ..models.s3_data_output import S3DataOutput

        name = self.name

        description = self.description

        external_id = self.external_id

        owner_id = str(self.owner_id)

        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        status = self.status.value

        configuration: dict[str, Any]
        if isinstance(self.configuration, S3DataOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, GlueDataOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, DatabricksDataOutput):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration.to_dict()

        source_aligned = self.source_aligned

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "external_id": external_id,
                "owner_id": owner_id,
                "platform_id": platform_id,
                "service_id": service_id,
                "status": status,
                "configuration": configuration,
                "sourceAligned": source_aligned,
                "tag_ids": tag_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.databricks_data_output import DatabricksDataOutput
        from ..models.glue_data_output import GlueDataOutput
        from ..models.s3_data_output import S3DataOutput
        from ..models.snowflake_data_output import SnowflakeDataOutput

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        external_id = d.pop("external_id")

        owner_id = UUID(d.pop("owner_id"))

        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

        status = DataOutputStatus(d.pop("status"))

        def _parse_configuration(
            data: object,
        ) -> Union[
            "DatabricksDataOutput",
            "GlueDataOutput",
            "S3DataOutput",
            "SnowflakeDataOutput",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0 = S3DataOutput.from_dict(data)

                return configuration_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_1 = GlueDataOutput.from_dict(data)

                return configuration_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_2 = DatabricksDataOutput.from_dict(data)

                return configuration_type_2
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            configuration_type_3 = SnowflakeDataOutput.from_dict(data)

            return configuration_type_3

        configuration = _parse_configuration(d.pop("configuration"))

        source_aligned = d.pop("sourceAligned")

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

        data_output_create = cls(
            name=name,
            description=description,
            external_id=external_id,
            owner_id=owner_id,
            platform_id=platform_id,
            service_id=service_id,
            status=status,
            configuration=configuration,
            source_aligned=source_aligned,
            tag_ids=tag_ids,
        )

        data_output_create.additional_properties = d
        return data_output_create

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
