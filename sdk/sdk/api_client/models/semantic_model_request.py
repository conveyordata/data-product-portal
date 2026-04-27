from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.semantic_model_format import SemanticModelFormat

if TYPE_CHECKING:
    from ..models.semantic_model_request_content import SemanticModelRequestContent


T = TypeVar("T", bound="SemanticModelRequest")


@_attrs_define
class SemanticModelRequest:
    """
    Attributes:
        name (str):
        format_ (SemanticModelFormat):
        content (SemanticModelRequestContent):
    """

    name: str
    format_: SemanticModelFormat
    content: SemanticModelRequestContent
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        format_ = self.format_.value

        content = self.content.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "format": format_,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.semantic_model_request_content import SemanticModelRequestContent

        d = dict(src_dict)
        name = d.pop("name")

        format_ = SemanticModelFormat(d.pop("format"))

        content = SemanticModelRequestContent.from_dict(d.pop("content"))

        semantic_model_request = cls(
            name=name,
            format_=format_,
            content=content,
        )

        semantic_model_request.additional_properties = d
        return semantic_model_request

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
