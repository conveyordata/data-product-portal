from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.abstract_data_product_status import AbstractDataProductStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain import Domain
    from ..models.user import User


T = TypeVar("T", bound="GetExplorationResponse")


@_attrs_define
class GetExplorationResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        domain (Domain):
        status (AbstractDataProductStatus):
        finalizers (list[str]):
        owner (None | User):
        deleted_owner_identifier (None | str | Unset):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain
    status: AbstractDataProductStatus
    finalizers: list[str]
    owner: None | User
    deleted_owner_identifier: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User  # noqa: PLC0415

        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        domain = self.domain.to_dict()

        status = self.status.value

        finalizers = self.finalizers

        owner: dict[str, Any] | None
        if isinstance(self.owner, User):
            owner = self.owner.to_dict()
        else:
            owner = self.owner

        deleted_owner_identifier: None | str | Unset
        if isinstance(self.deleted_owner_identifier, Unset):
            deleted_owner_identifier = UNSET
        else:
            deleted_owner_identifier = self.deleted_owner_identifier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "domain": domain,
                "status": status,
                "finalizers": finalizers,
                "owner": owner,
            }
        )
        if deleted_owner_identifier is not UNSET:
            field_dict["deleted_owner_identifier"] = deleted_owner_identifier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.domain import Domain  # noqa: PLC0415
        from ..models.user import User  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        domain = Domain.from_dict(d.pop("domain"))

        status = AbstractDataProductStatus(d.pop("status"))

        finalizers = cast(list[str], d.pop("finalizers"))

        def _parse_owner(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                owner_type_0 = User.from_dict(data)

                return owner_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        owner = _parse_owner(d.pop("owner"))

        def _parse_deleted_owner_identifier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deleted_owner_identifier = _parse_deleted_owner_identifier(
            d.pop("deleted_owner_identifier", UNSET)
        )

        get_exploration_response = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            domain=domain,
            status=status,
            finalizers=finalizers,
            owner=owner,
            deleted_owner_identifier=deleted_owner_identifier,
        )

        get_exploration_response.additional_properties = d
        return get_exploration_response

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
