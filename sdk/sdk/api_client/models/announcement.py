from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.announcement_type import AnnouncementType

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="Announcement")


@_attrs_define
class Announcement:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        type_ (AnnouncementType):
        title (str):
        message (str):
        link (None | str):
        author (None | User):
        created_at (datetime.datetime):
    """

    id: UUID
    output_port_id: UUID
    type_: AnnouncementType
    title: str
    message: str
    link: None | str
    author: None | User
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User  # noqa: PLC0415

        id = str(self.id)

        output_port_id = str(self.output_port_id)

        type_ = self.type_.value

        title = self.title

        message = self.message

        link: None | str
        link = self.link

        author: dict[str, Any] | None
        if isinstance(self.author, User):
            author = self.author.to_dict()
        else:
            author = self.author

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "type": type_,
                "title": title,
                "message": message,
                "link": link,
                "author": author,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        type_ = AnnouncementType(d.pop("type"))

        title = d.pop("title")

        message = d.pop("message")

        def _parse_link(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        link = _parse_link(d.pop("link"))

        def _parse_author(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                author_type_0 = User.from_dict(data)

                return author_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        author = _parse_author(d.pop("author"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        announcement = cls(
            id=id,
            output_port_id=output_port_id,
            type_=type_,
            title=title,
            message=message,
            link=link,
            author=author,
            created_at=created_at,
        )

        announcement.additional_properties = d
        return announcement

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
