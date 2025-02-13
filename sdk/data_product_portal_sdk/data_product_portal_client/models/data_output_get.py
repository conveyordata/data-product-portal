from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_output_status import DataOutputStatus

if TYPE_CHECKING:
    from ..models.base_data_product_get import BaseDataProductGet
    from ..models.databricks_data_output import DatabricksDataOutput
    from ..models.dataset_link import DatasetLink
    from ..models.glue_data_output import GlueDataOutput
    from ..models.s3_data_output import S3DataOutput
    from ..models.snowflake_data_output import SnowflakeDataOutput
    from ..models.tag import Tag


T = TypeVar("T", bound="DataOutputGet")


@_attrs_define
class DataOutputGet:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        external_id (str):
        owner (BaseDataProductGet):
        owner_id (UUID):
        platform_id (UUID):
        service_id (UUID):
        configuration (Union['DatabricksDataOutput', 'GlueDataOutput', 'S3DataOutput', 'SnowflakeDataOutput']):
        status (DataOutputStatus):
        dataset_links (list['DatasetLink']):
        tags (list['Tag']):
    """

    id: UUID
    name: str
    description: str
    external_id: str
    owner: "BaseDataProductGet"
    owner_id: UUID
    platform_id: UUID
    service_id: UUID
    configuration: Union[
        "DatabricksDataOutput", "GlueDataOutput", "S3DataOutput", "SnowflakeDataOutput"
    ]
    status: DataOutputStatus
    dataset_links: list["DatasetLink"]
    tags: list["Tag"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.databricks_data_output import DatabricksDataOutput
        from ..models.glue_data_output import GlueDataOutput
        from ..models.s3_data_output import S3DataOutput

        id = str(self.id)

        name = self.name

        description = self.description

        external_id = self.external_id

        owner = self.owner.to_dict()

        owner_id = str(self.owner_id)

        platform_id = str(self.platform_id)

        service_id = str(self.service_id)

        configuration: dict[str, Any]
        if isinstance(self.configuration, S3DataOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, GlueDataOutput):
            configuration = self.configuration.to_dict()
        elif isinstance(self.configuration, DatabricksDataOutput):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration.to_dict()

        status = self.status.value

        dataset_links = []
        for dataset_links_item_data in self.dataset_links:
            dataset_links_item = dataset_links_item_data.to_dict()
            dataset_links.append(dataset_links_item)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "external_id": external_id,
                "owner": owner,
                "owner_id": owner_id,
                "platform_id": platform_id,
                "service_id": service_id,
                "configuration": configuration,
                "status": status,
                "dataset_links": dataset_links,
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.base_data_product_get import BaseDataProductGet
        from ..models.databricks_data_output import DatabricksDataOutput
        from ..models.dataset_link import DatasetLink
        from ..models.glue_data_output import GlueDataOutput
        from ..models.s3_data_output import S3DataOutput
        from ..models.snowflake_data_output import SnowflakeDataOutput
        from ..models.tag import Tag

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        external_id = d.pop("external_id")

        owner = BaseDataProductGet.from_dict(d.pop("owner"))

        owner_id = UUID(d.pop("owner_id"))

        platform_id = UUID(d.pop("platform_id"))

        service_id = UUID(d.pop("service_id"))

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

        status = DataOutputStatus(d.pop("status"))

        dataset_links = []
        _dataset_links = d.pop("dataset_links")
        for dataset_links_item_data in _dataset_links:
            dataset_links_item = DatasetLink.from_dict(dataset_links_item_data)

            dataset_links.append(dataset_links_item)

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        data_output_get = cls(
            id=id,
            name=name,
            description=description,
            external_id=external_id,
            owner=owner,
            owner_id=owner_id,
            platform_id=platform_id,
            service_id=service_id,
            configuration=configuration,
            status=status,
            dataset_links=dataset_links,
            tags=tags,
        )

        data_output_get.additional_properties = d
        return data_output_get

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
