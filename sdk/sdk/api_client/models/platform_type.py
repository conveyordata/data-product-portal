from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.platform_type_kind import PlatformTypeKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.overridable_property import OverridableProperty


T = TypeVar("T", bound="PlatformType")


@_attrs_define
class PlatformType:
    """
    Attributes:
        kind (PlatformTypeKind):
        name (str):
        display_name (str):
        overridable_properties (list[OverridableProperty] | Unset):
    """

    kind: PlatformTypeKind
    name: str
    display_name: str
    overridable_properties: list[OverridableProperty] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        name = self.name

        display_name = self.display_name

        overridable_properties: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.overridable_properties, Unset):
            overridable_properties = []
            for overridable_properties_item_data in self.overridable_properties:
                overridable_properties_item = overridable_properties_item_data.to_dict()
                overridable_properties.append(overridable_properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "name": name,
                "display_name": display_name,
            }
        )
        if overridable_properties is not UNSET:
            field_dict["overridable_properties"] = overridable_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.overridable_property import OverridableProperty  # noqa: PLC0415

        d = dict(src_dict)
        kind = PlatformTypeKind(d.pop("kind"))

        name = d.pop("name")

        display_name = d.pop("display_name")

        _overridable_properties = d.pop("overridable_properties", UNSET)
        overridable_properties: list[OverridableProperty] | Unset = UNSET
        if _overridable_properties is not UNSET:
            overridable_properties = []
            for overridable_properties_item_data in _overridable_properties:
                overridable_properties_item = OverridableProperty.from_dict(
                    overridable_properties_item_data
                )

                overridable_properties.append(overridable_properties_item)

        platform_type = cls(
            kind=kind,
            name=name,
            display_name=display_name,
            overridable_properties=overridable_properties,
        )

        platform_type.additional_properties = d
        return platform_type

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
