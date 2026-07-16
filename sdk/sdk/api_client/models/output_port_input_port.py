from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.input_port_status import InputPortStatus
from ..models.renewal_status import RenewalStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.abstract_data_product_info import AbstractDataProductInfo
    from ..models.input_port_request_base import InputPortRequestBase


T = TypeVar("T", bound="OutputPortInputPort")


@_attrs_define
class OutputPortInputPort:
    """
    Attributes:
        id (UUID):
        status (InputPortStatus):
        current_request (InputPortRequestBase):
        consuming_abstract_data_product_id (UUID):
        consuming_abstract_data_product (AbstractDataProductInfo):
        renewal_status (None | RenewalStatus | Unset):
    """

    id: UUID
    status: InputPortStatus
    current_request: InputPortRequestBase
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product: AbstractDataProductInfo
    renewal_status: None | RenewalStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        status = self.status.value

        current_request = self.current_request.to_dict()

        consuming_abstract_data_product_id = str(
            self.consuming_abstract_data_product_id
        )

        consuming_abstract_data_product = self.consuming_abstract_data_product.to_dict()

        renewal_status: None | str | Unset
        if isinstance(self.renewal_status, Unset):
            renewal_status = UNSET
        elif isinstance(self.renewal_status, RenewalStatus):
            renewal_status = self.renewal_status.value
        else:
            renewal_status = self.renewal_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "current_request": current_request,
                "consuming_abstract_data_product_id": consuming_abstract_data_product_id,
                "consuming_abstract_data_product": consuming_abstract_data_product,
            }
        )
        if renewal_status is not UNSET:
            field_dict["renewal_status"] = renewal_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.abstract_data_product_info import AbstractDataProductInfo
        from ..models.input_port_request_base import InputPortRequestBase

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        status = InputPortStatus(d.pop("status"))

        current_request = InputPortRequestBase.from_dict(d.pop("current_request"))

        consuming_abstract_data_product_id = UUID(
            d.pop("consuming_abstract_data_product_id")
        )

        consuming_abstract_data_product = AbstractDataProductInfo.from_dict(
            d.pop("consuming_abstract_data_product")
        )

        def _parse_renewal_status(data: object) -> None | RenewalStatus | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                renewal_status_type_0 = RenewalStatus(data)

                return renewal_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RenewalStatus | Unset, data)

        renewal_status = _parse_renewal_status(d.pop("renewal_status", UNSET))

        output_port_input_port = cls(
            id=id,
            status=status,
            current_request=current_request,
            consuming_abstract_data_product_id=consuming_abstract_data_product_id,
            consuming_abstract_data_product=consuming_abstract_data_product,
            renewal_status=renewal_status,
        )

        output_port_input_port.additional_properties = d
        return output_port_input_port

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
