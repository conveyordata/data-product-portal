import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.data_product_membership_status import DataProductMembershipStatus
from ..models.data_product_user_role import DataProductUserRole

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="DataProductMembership")


@_attrs_define
class DataProductMembership:
    """
    Attributes:
        user_id (UUID):
        role (DataProductUserRole):
        id (UUID):
        data_product_id (UUID):
        status (DataProductMembershipStatus):
        requested_on (datetime.datetime):
        requested_by (Union['User', None]):
        approved_by (Union['User', None]):
        approved_on (Union[None, datetime.datetime]):
        denied_by (Union['User', None]):
        denied_on (Union[None, datetime.datetime]):
    """

    user_id: UUID
    role: DataProductUserRole
    id: UUID
    data_product_id: UUID
    status: DataProductMembershipStatus
    requested_on: datetime.datetime
    requested_by: Union["User", None]
    approved_by: Union["User", None]
    approved_on: Union[None, datetime.datetime]
    denied_by: Union["User", None]
    denied_on: Union[None, datetime.datetime]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        user_id = str(self.user_id)

        role = self.role.value

        id = str(self.id)

        data_product_id = str(self.data_product_id)

        status = self.status.value

        requested_on = self.requested_on.isoformat()

        requested_by: Union[None, dict[str, Any]]
        if isinstance(self.requested_by, User):
            requested_by = self.requested_by.to_dict()
        else:
            requested_by = self.requested_by

        approved_by: Union[None, dict[str, Any]]
        if isinstance(self.approved_by, User):
            approved_by = self.approved_by.to_dict()
        else:
            approved_by = self.approved_by

        approved_on: Union[None, str]
        if isinstance(self.approved_on, datetime.datetime):
            approved_on = self.approved_on.isoformat()
        else:
            approved_on = self.approved_on

        denied_by: Union[None, dict[str, Any]]
        if isinstance(self.denied_by, User):
            denied_by = self.denied_by.to_dict()
        else:
            denied_by = self.denied_by

        denied_on: Union[None, str]
        if isinstance(self.denied_on, datetime.datetime):
            denied_on = self.denied_on.isoformat()
        else:
            denied_on = self.denied_on

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "role": role,
                "id": id,
                "data_product_id": data_product_id,
                "status": status,
                "requested_on": requested_on,
                "requested_by": requested_by,
                "approved_by": approved_by,
                "approved_on": approved_on,
                "denied_by": denied_by,
                "denied_on": denied_on,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.user import User

        d = src_dict.copy()
        user_id = UUID(d.pop("user_id"))

        role = DataProductUserRole(d.pop("role"))

        id = UUID(d.pop("id"))

        data_product_id = UUID(d.pop("data_product_id"))

        status = DataProductMembershipStatus(d.pop("status"))

        requested_on = isoparse(d.pop("requested_on"))

        def _parse_requested_by(data: object) -> Union["User", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                requested_by_type_0 = User.from_dict(data)

                return requested_by_type_0
            except:  # noqa: E722
                pass
            return cast(Union["User", None], data)

        requested_by = _parse_requested_by(d.pop("requested_by"))

        def _parse_approved_by(data: object) -> Union["User", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                approved_by_type_0 = User.from_dict(data)

                return approved_by_type_0
            except:  # noqa: E722
                pass
            return cast(Union["User", None], data)

        approved_by = _parse_approved_by(d.pop("approved_by"))

        def _parse_approved_on(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                approved_on_type_0 = isoparse(data)

                return approved_on_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        approved_on = _parse_approved_on(d.pop("approved_on"))

        def _parse_denied_by(data: object) -> Union["User", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                denied_by_type_0 = User.from_dict(data)

                return denied_by_type_0
            except:  # noqa: E722
                pass
            return cast(Union["User", None], data)

        denied_by = _parse_denied_by(d.pop("denied_by"))

        def _parse_denied_on(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                denied_on_type_0 = isoparse(data)

                return denied_on_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        denied_on = _parse_denied_on(d.pop("denied_on"))

        data_product_membership = cls(
            user_id=user_id,
            role=role,
            id=id,
            data_product_id=data_product_id,
            status=status,
            requested_on=requested_on,
            requested_by=requested_by,
            approved_by=approved_by,
            approved_on=approved_on,
            denied_by=denied_by,
            denied_on=denied_on,
        )

        data_product_membership.additional_properties = d
        return data_product_membership

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
