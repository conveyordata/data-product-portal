from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ui_element_metadata import UIElementMetadata


T = TypeVar("T", bound="EnvironmentUIMetadata")


@_attrs_define
class EnvironmentUIMetadata:
    """
    Attributes:
        environment_id (UUID):
        ui_metadata (list[UIElementMetadata]):
    """

    environment_id: UUID
    ui_metadata: list[UIElementMetadata]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_id = str(self.environment_id)

        ui_metadata = []
        for ui_metadata_item_data in self.ui_metadata:
            ui_metadata_item = ui_metadata_item_data.to_dict()
            ui_metadata.append(ui_metadata_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_id": environment_id,
                "ui_metadata": ui_metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ui_element_metadata import UIElementMetadata  # noqa: PLC0415

        d = dict(src_dict)
        environment_id = UUID(d.pop("environment_id"))

        ui_metadata = []
        _ui_metadata = d.pop("ui_metadata")
        for ui_metadata_item_data in _ui_metadata:
            ui_metadata_item = UIElementMetadata.from_dict(ui_metadata_item_data)

            ui_metadata.append(ui_metadata_item)

        environment_ui_metadata = cls(
            environment_id=environment_id,
            ui_metadata=ui_metadata,
        )

        environment_ui_metadata.additional_properties = d
        return environment_ui_metadata

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
