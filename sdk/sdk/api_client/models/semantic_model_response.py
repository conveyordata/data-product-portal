from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.semantic_model_format import SemanticModelFormat

if TYPE_CHECKING:
    from ..models.semantic_model_response_content import SemanticModelResponseContent


T = TypeVar("T", bound="SemanticModelResponse")


@_attrs_define
class SemanticModelResponse:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        name (str):
        format_ (SemanticModelFormat):
        content (SemanticModelResponseContent):
    """

    id: UUID
    output_port_id: UUID
    name: str
    format_: SemanticModelFormat
    content: SemanticModelResponseContent
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        name = self.name

        format_ = self.format_.value

        content = self.content.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "name": name,
                "format": format_,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.semantic_model_response_content import (
            SemanticModelResponseContent,
        )

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        name = d.pop("name")

        format_ = SemanticModelFormat(d.pop("format"))

        content = SemanticModelResponseContent.from_dict(d.pop("content"))

        semantic_model_response = cls(
            id=id,
            output_port_id=output_port_id,
            name=name,
            format_=format_,
            content=content,
        )

        semantic_model_response.additional_properties = d
        return semantic_model_response

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
