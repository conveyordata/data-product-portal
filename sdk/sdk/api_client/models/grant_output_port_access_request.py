from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GrantOutputPortAccessRequest")


@_attrs_define
class GrantOutputPortAccessRequest:
    """
    Attributes:
        consuming_abstract_data_product_id (UUID):
        justification (str):
        access_mode_id (None | Unset | UUID):
    """

    consuming_abstract_data_product_id: UUID
    justification: str
    access_mode_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        consuming_abstract_data_product_id = str(
            self.consuming_abstract_data_product_id
        )

        justification = self.justification

        access_mode_id: None | str | Unset
        if isinstance(self.access_mode_id, Unset):
            access_mode_id = UNSET
        elif isinstance(self.access_mode_id, UUID):
            access_mode_id = str(self.access_mode_id)
        else:
            access_mode_id = self.access_mode_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "consuming_abstract_data_product_id": consuming_abstract_data_product_id,
                "justification": justification,
            }
        )
        if access_mode_id is not UNSET:
            field_dict["access_mode_id"] = access_mode_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        consuming_abstract_data_product_id = UUID(
            d.pop("consuming_abstract_data_product_id")
        )

        justification = d.pop("justification")

        def _parse_access_mode_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                access_mode_id_type_0 = UUID(data)

                return access_mode_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        access_mode_id = _parse_access_mode_id(d.pop("access_mode_id", UNSET))

        grant_output_port_access_request = cls(
            consuming_abstract_data_product_id=consuming_abstract_data_product_id,
            justification=justification,
            access_mode_id=access_mode_id,
        )

        grant_output_port_access_request.additional_properties = d
        return grant_output_port_access_request

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
