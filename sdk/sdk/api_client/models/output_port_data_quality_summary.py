from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.data_quality_status import DataQualityStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_quality_technical_asset import DataQualityTechnicalAsset
    from ..models.output_port_data_quality_summary_dimensions_type_0 import (
        OutputPortDataQualitySummaryDimensionsType0,
    )


T = TypeVar("T", bound="OutputPortDataQualitySummary")


@_attrs_define
class OutputPortDataQualitySummary:
    """
    Attributes:
        created_at (datetime.datetime):
        overall_status (DataQualityStatus):
        technical_assets (list[DataQualityTechnicalAsset]):
        description (None | str | Unset):
        details_url (None | str | Unset):
        dimensions (None | OutputPortDataQualitySummaryDimensionsType0 | Unset):
    """

    created_at: datetime.datetime
    overall_status: DataQualityStatus
    technical_assets: list[DataQualityTechnicalAsset]
    description: None | str | Unset = UNSET
    details_url: None | str | Unset = UNSET
    dimensions: None | OutputPortDataQualitySummaryDimensionsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.output_port_data_quality_summary_dimensions_type_0 import (
            OutputPortDataQualitySummaryDimensionsType0,
        )

        created_at = self.created_at.isoformat()

        overall_status = self.overall_status.value

        technical_assets = []
        for technical_assets_item_data in self.technical_assets:
            technical_assets_item = technical_assets_item_data.to_dict()
            technical_assets.append(technical_assets_item)

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        details_url: None | str | Unset
        if isinstance(self.details_url, Unset):
            details_url = UNSET
        else:
            details_url = self.details_url

        dimensions: dict[str, Any] | None | Unset
        if isinstance(self.dimensions, Unset):
            dimensions = UNSET
        elif isinstance(self.dimensions, OutputPortDataQualitySummaryDimensionsType0):
            dimensions = self.dimensions.to_dict()
        else:
            dimensions = self.dimensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "overall_status": overall_status,
                "technical_assets": technical_assets,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if details_url is not UNSET:
            field_dict["details_url"] = details_url
        if dimensions is not UNSET:
            field_dict["dimensions"] = dimensions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_quality_technical_asset import DataQualityTechnicalAsset
        from ..models.output_port_data_quality_summary_dimensions_type_0 import (
            OutputPortDataQualitySummaryDimensionsType0,
        )

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        overall_status = DataQualityStatus(d.pop("overall_status"))

        technical_assets = []
        _technical_assets = d.pop("technical_assets")
        for technical_assets_item_data in _technical_assets:
            technical_assets_item = DataQualityTechnicalAsset.from_dict(
                technical_assets_item_data
            )

            technical_assets.append(technical_assets_item)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_details_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        details_url = _parse_details_url(d.pop("details_url", UNSET))

        def _parse_dimensions(
            data: object,
        ) -> None | OutputPortDataQualitySummaryDimensionsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                dimensions_type_0 = (
                    OutputPortDataQualitySummaryDimensionsType0.from_dict(data)
                )

                return dimensions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | OutputPortDataQualitySummaryDimensionsType0 | Unset, data
            )

        dimensions = _parse_dimensions(d.pop("dimensions", UNSET))

        output_port_data_quality_summary = cls(
            created_at=created_at,
            overall_status=overall_status,
            technical_assets=technical_assets,
            description=description,
            details_url=details_url,
            dimensions=dimensions,
        )

        output_port_data_quality_summary.additional_properties = d
        return output_port_data_quality_summary

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
