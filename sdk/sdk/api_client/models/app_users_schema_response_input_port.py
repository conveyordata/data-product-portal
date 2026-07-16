from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.abstract_data_product_info import AbstractDataProductInfo
    from ..models.output_port import OutputPort


T = TypeVar("T", bound="AppUsersSchemaResponseInputPort")


@_attrs_define
class AppUsersSchemaResponseInputPort:
    """
    Attributes:
        consuming_abstract_data_product_id (UUID):
        consuming_abstract_data_product (AbstractDataProductInfo):
        output_port_id (UUID):
        output_port (OutputPort):
    """

    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product: AbstractDataProductInfo
    output_port_id: UUID
    output_port: OutputPort
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        consuming_abstract_data_product_id = str(
            self.consuming_abstract_data_product_id
        )

        consuming_abstract_data_product = self.consuming_abstract_data_product.to_dict()

        output_port_id = str(self.output_port_id)

        output_port = self.output_port.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "consuming_abstract_data_product_id": consuming_abstract_data_product_id,
                "consuming_abstract_data_product": consuming_abstract_data_product,
                "output_port_id": output_port_id,
                "output_port": output_port,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.abstract_data_product_info import AbstractDataProductInfo
        from ..models.output_port import OutputPort

        d = dict(src_dict)
        consuming_abstract_data_product_id = UUID(
            d.pop("consuming_abstract_data_product_id")
        )

        consuming_abstract_data_product = AbstractDataProductInfo.from_dict(
            d.pop("consuming_abstract_data_product")
        )

        output_port_id = UUID(d.pop("output_port_id"))

        output_port = OutputPort.from_dict(d.pop("output_port"))

        app_users_schema_response_input_port = cls(
            consuming_abstract_data_product_id=consuming_abstract_data_product_id,
            consuming_abstract_data_product=consuming_abstract_data_product,
            output_port_id=output_port_id,
            output_port=output_port,
        )

        app_users_schema_response_input_port.additional_properties = d
        return app_users_schema_response_input_port

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
