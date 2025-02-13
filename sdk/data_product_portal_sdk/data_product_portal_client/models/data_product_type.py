from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_icon_key import DataProductIconKey

if TYPE_CHECKING:
    from ..models.data_product import DataProduct


T = TypeVar("T", bound="DataProductType")


@_attrs_define
class DataProductType:
    """
    Attributes:
        name (str):
        description (str):
        icon_key (DataProductIconKey):
        id (UUID):
        data_products (list['DataProduct']):
    """

    name: str
    description: str
    icon_key: DataProductIconKey
    id: UUID
    data_products: list["DataProduct"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        icon_key = self.icon_key.value

        id = str(self.id)

        data_products = []
        for data_products_item_data in self.data_products:
            data_products_item = data_products_item_data.to_dict()
            data_products.append(data_products_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "icon_key": icon_key,
                "id": id,
                "data_products": data_products,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_product import DataProduct

        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        icon_key = DataProductIconKey(d.pop("icon_key"))

        id = UUID(d.pop("id"))

        data_products = []
        _data_products = d.pop("data_products")
        for data_products_item_data in _data_products:
            data_products_item = DataProduct.from_dict(data_products_item_data)

            data_products.append(data_products_item)

        data_product_type = cls(
            name=name,
            description=description,
            icon_key=icon_key,
            id=id,
            data_products=data_products,
        )

        data_product_type.additional_properties = d
        return data_product_type

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
