from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_product_setting import DataProductSetting


T = TypeVar("T", bound="DataProductSettingValue")


@_attrs_define
class DataProductSettingValue:
    """
    Attributes:
        data_product_setting_id (UUID):
        value (str):
        id (UUID):
        data_product_setting (DataProductSetting):
        data_product_id (Union[None, UUID, Unset]):
        dataset_id (Union[None, UUID, Unset]):
    """

    data_product_setting_id: UUID
    value: str
    id: UUID
    data_product_setting: "DataProductSetting"
    data_product_id: Union[None, UUID, Unset] = UNSET
    dataset_id: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_setting_id = str(self.data_product_setting_id)

        value = self.value

        id = str(self.id)

        data_product_setting = self.data_product_setting.to_dict()

        data_product_id: Union[None, Unset, str]
        if isinstance(self.data_product_id, Unset):
            data_product_id = UNSET
        elif isinstance(self.data_product_id, UUID):
            data_product_id = str(self.data_product_id)
        else:
            data_product_id = self.data_product_id

        dataset_id: Union[None, Unset, str]
        if isinstance(self.dataset_id, Unset):
            dataset_id = UNSET
        elif isinstance(self.dataset_id, UUID):
            dataset_id = str(self.dataset_id)
        else:
            dataset_id = self.dataset_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_setting_id": data_product_setting_id,
                "value": value,
                "id": id,
                "data_product_setting": data_product_setting,
            }
        )
        if data_product_id is not UNSET:
            field_dict["data_product_id"] = data_product_id
        if dataset_id is not UNSET:
            field_dict["dataset_id"] = dataset_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_product_setting import DataProductSetting

        d = src_dict.copy()
        data_product_setting_id = UUID(d.pop("data_product_setting_id"))

        value = d.pop("value")

        id = UUID(d.pop("id"))

        data_product_setting = DataProductSetting.from_dict(
            d.pop("data_product_setting")
        )

        def _parse_data_product_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                data_product_id_type_0 = UUID(data)

                return data_product_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        data_product_id = _parse_data_product_id(d.pop("data_product_id", UNSET))

        def _parse_dataset_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                dataset_id_type_0 = UUID(data)

                return dataset_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        dataset_id = _parse_dataset_id(d.pop("dataset_id", UNSET))

        data_product_setting_value = cls(
            data_product_setting_id=data_product_setting_id,
            value=value,
            id=id,
            data_product_setting=data_product_setting,
            data_product_id=data_product_id,
            dataset_id=dataset_id,
        )

        data_product_setting_value.additional_properties = d
        return data_product_setting_value

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
