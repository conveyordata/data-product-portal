from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T",
    bound="UpdateDataProductLifecycleApiDataProductLifecyclesIdPutResponseUpdateDataProductLifecycleApiDataProductLifecyclesIdPut",
)


@_attrs_define
class UpdateDataProductLifecycleApiDataProductLifecyclesIdPutResponseUpdateDataProductLifecycleApiDataProductLifecyclesIdPut:
    """ """

    additional_properties: dict[str, UUID] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = str(prop)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        update_data_product_lifecycle_api_data_product_lifecycles_id_put_response_update_data_product_lifecycle_api_data_product_lifecycles_id_put = (
            cls()
        )

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = UUID(prop_dict)

            additional_properties[prop_name] = additional_property

        update_data_product_lifecycle_api_data_product_lifecycles_id_put_response_update_data_product_lifecycle_api_data_product_lifecycles_id_put.additional_properties = (
            additional_properties
        )
        return update_data_product_lifecycle_api_data_product_lifecycles_id_put_response_update_data_product_lifecycle_api_data_product_lifecycles_id_put

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> UUID:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: UUID) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
