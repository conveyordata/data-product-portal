from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (UUID):
        email (str):
        external_id (str):
        first_name (str):
        last_name (str):
        has_seen_tour (bool):
        can_become_admin (bool):
        admin_expiry (datetime.datetime | None | Unset):
    """

    id: UUID
    email: str
    external_id: str
    first_name: str
    last_name: str
    has_seen_tour: bool
    can_become_admin: bool
    admin_expiry: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        email = self.email

        external_id = self.external_id

        first_name = self.first_name

        last_name = self.last_name

        has_seen_tour = self.has_seen_tour

        can_become_admin = self.can_become_admin

        admin_expiry: None | str | Unset
        if isinstance(self.admin_expiry, Unset):
            admin_expiry = UNSET
        elif isinstance(self.admin_expiry, datetime.datetime):
            admin_expiry = self.admin_expiry.isoformat()
        else:
            admin_expiry = self.admin_expiry

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "external_id": external_id,
                "first_name": first_name,
                "last_name": last_name,
                "has_seen_tour": has_seen_tour,
                "can_become_admin": can_become_admin,
            }
        )
        if admin_expiry is not UNSET:
            field_dict["admin_expiry"] = admin_expiry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        email = d.pop("email")

        external_id = d.pop("external_id")

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        has_seen_tour = d.pop("has_seen_tour")

        can_become_admin = d.pop("can_become_admin")

        def _parse_admin_expiry(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                admin_expiry_type_0 = isoparse(data)

                return admin_expiry_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        admin_expiry = _parse_admin_expiry(d.pop("admin_expiry", UNSET))

        user = cls(
            id=id,
            email=email,
            external_id=external_id,
            first_name=first_name,
            last_name=last_name,
            has_seen_tour=has_seen_tour,
            can_become_admin=can_become_admin,
            admin_expiry=admin_expiry,
        )

        user.additional_properties = d
        return user

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
