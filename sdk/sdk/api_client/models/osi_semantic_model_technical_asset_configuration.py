from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OSISemanticModelTechnicalAssetConfiguration")


@_attrs_define
class OSISemanticModelTechnicalAssetConfiguration:
    """
    Attributes:
        configuration_type (Literal['OSISemanticModelTechnicalAssetConfiguration']):
        model_name (str | Unset):  Default: ''.
        location (str | Unset):  Default: ''.
    """

    configuration_type: Literal["OSISemanticModelTechnicalAssetConfiguration"]
    model_name: str | Unset = ""
    location: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        model_name = self.model_name

        location = self.location

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration_type": configuration_type,
            }
        )
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if location is not UNSET:
            field_dict["location"] = location

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        configuration_type = cast(
            Literal["OSISemanticModelTechnicalAssetConfiguration"],
            d.pop("configuration_type"),
        )
        if configuration_type != "OSISemanticModelTechnicalAssetConfiguration":
            raise ValueError(
                f"configuration_type must match const 'OSISemanticModelTechnicalAssetConfiguration', got '{configuration_type}'"
            )

        model_name = d.pop("model_name", UNSET)

        location = d.pop("location", UNSET)

        osi_semantic_model_technical_asset_configuration = cls(
            configuration_type=configuration_type,
            model_name=model_name,
            location=location,
        )

        osi_semantic_model_technical_asset_configuration.additional_properties = d
        return osi_semantic_model_technical_asset_configuration

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
