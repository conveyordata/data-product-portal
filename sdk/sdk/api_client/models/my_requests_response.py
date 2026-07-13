from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_role_assignment_request import (
        DataProductRoleAssignmentRequest,
    )
    from ..models.input_port_request import InputPortRequest
    from ..models.technical_asset_output_port_request import (
        TechnicalAssetOutputPortRequest,
    )


T = TypeVar("T", bound="MyRequestsResponse")


@_attrs_define
class MyRequestsResponse:
    """
    Attributes:
        my_requests (list[DataProductRoleAssignmentRequest | InputPortRequest | TechnicalAssetOutputPortRequest]):
    """

    my_requests: list[
        DataProductRoleAssignmentRequest
        | InputPortRequest
        | TechnicalAssetOutputPortRequest
    ]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.input_port_request import InputPortRequest
        from ..models.technical_asset_output_port_request import (
            TechnicalAssetOutputPortRequest,
        )

        my_requests = []
        for my_requests_item_data in self.my_requests:
            my_requests_item: dict[str, Any]
            if isinstance(my_requests_item_data, InputPortRequest):
                my_requests_item = my_requests_item_data.to_dict()
            elif isinstance(my_requests_item_data, TechnicalAssetOutputPortRequest):
                my_requests_item = my_requests_item_data.to_dict()
            else:
                my_requests_item = my_requests_item_data.to_dict()

            my_requests.append(my_requests_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "my_requests": my_requests,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_role_assignment_request import (
            DataProductRoleAssignmentRequest,
        )
        from ..models.input_port_request import InputPortRequest
        from ..models.technical_asset_output_port_request import (
            TechnicalAssetOutputPortRequest,
        )

        d = dict(src_dict)
        my_requests = []
        _my_requests = d.pop("my_requests")
        for my_requests_item_data in _my_requests:

            def _parse_my_requests_item(
                data: object,
            ) -> (
                DataProductRoleAssignmentRequest
                | InputPortRequest
                | TechnicalAssetOutputPortRequest
            ):
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    my_requests_item_type_0 = InputPortRequest.from_dict(data)

                    return my_requests_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    my_requests_item_type_1 = TechnicalAssetOutputPortRequest.from_dict(
                        data
                    )

                    return my_requests_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                my_requests_item_type_2 = DataProductRoleAssignmentRequest.from_dict(
                    data
                )

                return my_requests_item_type_2

            my_requests_item = _parse_my_requests_item(my_requests_item_data)

            my_requests.append(my_requests_item)

        my_requests_response = cls(
            my_requests=my_requests,
        )

        my_requests_response.additional_properties = d
        return my_requests_response

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
