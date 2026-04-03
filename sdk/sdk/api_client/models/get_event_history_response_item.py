from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.event_entity_type import EventEntityType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_product import DataProduct
    from ..models.output_port import OutputPort
    from ..models.technical_asset import TechnicalAsset
    from ..models.user import User


T = TypeVar("T", bound="GetEventHistoryResponseItem")


@_attrs_define
class GetEventHistoryResponseItem:
    """
    Attributes:
        id (UUID):
        name (str):
        subject_id (UUID):
        subject_type (EventEntityType):
        actor_id (UUID):
        created_on (datetime.datetime):
        actor (User):
        target_id (None | Unset | UUID):
        target_type (EventEntityType | None | Unset):
        deleted_subject_identifier (None | str | Unset):
        deleted_target_identifier (None | str | Unset):
        data_product (DataProduct | None | Unset):
        user (None | Unset | User):
        output_port (None | OutputPort | Unset):
        technical_asset (None | TechnicalAsset | Unset):
    """

    id: UUID
    name: str
    subject_id: UUID
    subject_type: EventEntityType
    actor_id: UUID
    created_on: datetime.datetime
    actor: User
    target_id: None | Unset | UUID = UNSET
    target_type: EventEntityType | None | Unset = UNSET
    deleted_subject_identifier: None | str | Unset = UNSET
    deleted_target_identifier: None | str | Unset = UNSET
    data_product: DataProduct | None | Unset = UNSET
    user: None | Unset | User = UNSET
    output_port: None | OutputPort | Unset = UNSET
    technical_asset: None | TechnicalAsset | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product import DataProduct
        from ..models.output_port import OutputPort
        from ..models.technical_asset import TechnicalAsset
        from ..models.user import User

        id = str(self.id)

        name = self.name

        subject_id = str(self.subject_id)

        subject_type = self.subject_type.value

        actor_id = str(self.actor_id)

        created_on = self.created_on.isoformat()

        actor = self.actor.to_dict()

        target_id: None | str | Unset
        if isinstance(self.target_id, Unset):
            target_id = UNSET
        elif isinstance(self.target_id, UUID):
            target_id = str(self.target_id)
        else:
            target_id = self.target_id

        target_type: None | str | Unset
        if isinstance(self.target_type, Unset):
            target_type = UNSET
        elif isinstance(self.target_type, EventEntityType):
            target_type = self.target_type.value
        else:
            target_type = self.target_type

        deleted_subject_identifier: None | str | Unset
        if isinstance(self.deleted_subject_identifier, Unset):
            deleted_subject_identifier = UNSET
        else:
            deleted_subject_identifier = self.deleted_subject_identifier

        deleted_target_identifier: None | str | Unset
        if isinstance(self.deleted_target_identifier, Unset):
            deleted_target_identifier = UNSET
        else:
            deleted_target_identifier = self.deleted_target_identifier

        data_product: dict[str, Any] | None | Unset
        if isinstance(self.data_product, Unset):
            data_product = UNSET
        elif isinstance(self.data_product, DataProduct):
            data_product = self.data_product.to_dict()
        else:
            data_product = self.data_product

        user: dict[str, Any] | None | Unset
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, User):
            user = self.user.to_dict()
        else:
            user = self.user

        output_port: dict[str, Any] | None | Unset
        if isinstance(self.output_port, Unset):
            output_port = UNSET
        elif isinstance(self.output_port, OutputPort):
            output_port = self.output_port.to_dict()
        else:
            output_port = self.output_port

        technical_asset: dict[str, Any] | None | Unset
        if isinstance(self.technical_asset, Unset):
            technical_asset = UNSET
        elif isinstance(self.technical_asset, TechnicalAsset):
            technical_asset = self.technical_asset.to_dict()
        else:
            technical_asset = self.technical_asset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "subject_id": subject_id,
                "subject_type": subject_type,
                "actor_id": actor_id,
                "created_on": created_on,
                "actor": actor,
            }
        )
        if target_id is not UNSET:
            field_dict["target_id"] = target_id
        if target_type is not UNSET:
            field_dict["target_type"] = target_type
        if deleted_subject_identifier is not UNSET:
            field_dict["deleted_subject_identifier"] = deleted_subject_identifier
        if deleted_target_identifier is not UNSET:
            field_dict["deleted_target_identifier"] = deleted_target_identifier
        if data_product is not UNSET:
            field_dict["data_product"] = data_product
        if user is not UNSET:
            field_dict["user"] = user
        if output_port is not UNSET:
            field_dict["output_port"] = output_port
        if technical_asset is not UNSET:
            field_dict["technical_asset"] = technical_asset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product import DataProduct
        from ..models.output_port import OutputPort
        from ..models.technical_asset import TechnicalAsset
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        subject_id = UUID(d.pop("subject_id"))

        subject_type = EventEntityType(d.pop("subject_type"))

        actor_id = UUID(d.pop("actor_id"))

        created_on = isoparse(d.pop("created_on"))

        actor = User.from_dict(d.pop("actor"))

        def _parse_target_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                target_id_type_0 = UUID(data)

                return target_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        target_id = _parse_target_id(d.pop("target_id", UNSET))

        def _parse_target_type(data: object) -> EventEntityType | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                target_type_type_0 = EventEntityType(data)

                return target_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EventEntityType | None | Unset, data)

        target_type = _parse_target_type(d.pop("target_type", UNSET))

        def _parse_deleted_subject_identifier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deleted_subject_identifier = _parse_deleted_subject_identifier(
            d.pop("deleted_subject_identifier", UNSET)
        )

        def _parse_deleted_target_identifier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deleted_target_identifier = _parse_deleted_target_identifier(
            d.pop("deleted_target_identifier", UNSET)
        )

        def _parse_data_product(data: object) -> DataProduct | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_product_type_0 = DataProduct.from_dict(data)

                return data_product_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataProduct | None | Unset, data)

        data_product = _parse_data_product(d.pop("data_product", UNSET))

        def _parse_user(data: object) -> None | Unset | User:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_type_0 = User.from_dict(data)

                return user_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | User, data)

        user = _parse_user(d.pop("user", UNSET))

        def _parse_output_port(data: object) -> None | OutputPort | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_port_type_0 = OutputPort.from_dict(data)

                return output_port_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OutputPort | Unset, data)

        output_port = _parse_output_port(d.pop("output_port", UNSET))

        def _parse_technical_asset(data: object) -> None | TechnicalAsset | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                technical_asset_type_0 = TechnicalAsset.from_dict(data)

                return technical_asset_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TechnicalAsset | Unset, data)

        technical_asset = _parse_technical_asset(d.pop("technical_asset", UNSET))

        get_event_history_response_item = cls(
            id=id,
            name=name,
            subject_id=subject_id,
            subject_type=subject_type,
            actor_id=actor_id,
            created_on=created_on,
            actor=actor,
            target_id=target_id,
            target_type=target_type,
            deleted_subject_identifier=deleted_subject_identifier,
            deleted_target_identifier=deleted_target_identifier,
            data_product=data_product,
            user=user,
            output_port=output_port,
            technical_asset=technical_asset,
        )

        get_event_history_response_item.additional_properties = d
        return get_event_history_response_item

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
