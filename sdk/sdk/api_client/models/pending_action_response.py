from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_output_port_pending_action import (
        DataProductOutputPortPendingAction,
    )
    from ..models.data_product_role_assignment_pending_action import (
        DataProductRoleAssignmentPendingAction,
    )
    from ..models.technical_asset_output_port_pending_action import (
        TechnicalAssetOutputPortPendingAction,
    )


T = TypeVar("T", bound="PendingActionResponse")


@_attrs_define
class PendingActionResponse:
    """
    Attributes:
        pending_actions (list[DataProductOutputPortPendingAction | DataProductRoleAssignmentPendingAction |
            TechnicalAssetOutputPortPendingAction]):
    """

    pending_actions: list[
        DataProductOutputPortPendingAction
        | DataProductRoleAssignmentPendingAction
        | TechnicalAssetOutputPortPendingAction
    ]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_output_port_pending_action import (
            DataProductOutputPortPendingAction,
        )
        from ..models.technical_asset_output_port_pending_action import (
            TechnicalAssetOutputPortPendingAction,
        )

        pending_actions = []
        for pending_actions_item_data in self.pending_actions:
            pending_actions_item: dict[str, Any]
            if isinstance(
                pending_actions_item_data, DataProductOutputPortPendingAction
            ):
                pending_actions_item = pending_actions_item_data.to_dict()
            elif isinstance(
                pending_actions_item_data, TechnicalAssetOutputPortPendingAction
            ):
                pending_actions_item = pending_actions_item_data.to_dict()
            else:
                pending_actions_item = pending_actions_item_data.to_dict()

            pending_actions.append(pending_actions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pending_actions": pending_actions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_output_port_pending_action import (
            DataProductOutputPortPendingAction,
        )
        from ..models.data_product_role_assignment_pending_action import (
            DataProductRoleAssignmentPendingAction,
        )
        from ..models.technical_asset_output_port_pending_action import (
            TechnicalAssetOutputPortPendingAction,
        )

        d = dict(src_dict)
        pending_actions = []
        _pending_actions = d.pop("pending_actions")
        for pending_actions_item_data in _pending_actions:

            def _parse_pending_actions_item(
                data: object,
            ) -> (
                DataProductOutputPortPendingAction
                | DataProductRoleAssignmentPendingAction
                | TechnicalAssetOutputPortPendingAction
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    pending_actions_item_type_0 = (
                        DataProductOutputPortPendingAction.from_dict(data)
                    )

                    return pending_actions_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    pending_actions_item_type_1 = (
                        TechnicalAssetOutputPortPendingAction.from_dict(data)
                    )

                    return pending_actions_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                pending_actions_item_type_2 = (
                    DataProductRoleAssignmentPendingAction.from_dict(data)
                )

                return pending_actions_item_type_2

            pending_actions_item = _parse_pending_actions_item(
                pending_actions_item_data
            )

            pending_actions.append(pending_actions_item)

        pending_action_response = cls(
            pending_actions=pending_actions,
        )

        pending_action_response.additional_properties = d
        return pending_action_response

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
