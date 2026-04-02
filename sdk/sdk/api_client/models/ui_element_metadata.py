from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ui_element_type import UIElementType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_dependency import FieldDependency
    from ..models.ui_element_checkbox import UIElementCheckbox
    from ..models.ui_element_radio import UIElementRadio
    from ..models.ui_element_select import UIElementSelect
    from ..models.ui_element_string import UIElementString


T = TypeVar("T", bound="UIElementMetadata")


@_attrs_define
class UIElementMetadata:
    """
    Attributes:
        label (str):
        type_ (UIElementType):
        required (bool):
        name (str):
        tooltip (None | str | Unset):
        hidden (bool | None | Unset):
        checkbox (None | UIElementCheckbox | Unset):
        select (None | UIElementSelect | Unset):
        string (None | UIElementString | Unset):
        radio (None | UIElementRadio | Unset):
        depends_on (list[FieldDependency] | None | Unset):
        disabled (bool | None | Unset):
        use_namespace_when_not_source_aligned (bool | None | Unset):
    """

    label: str
    type_: UIElementType
    required: bool
    name: str
    tooltip: None | str | Unset = UNSET
    hidden: bool | None | Unset = UNSET
    checkbox: None | UIElementCheckbox | Unset = UNSET
    select: None | UIElementSelect | Unset = UNSET
    string: None | UIElementString | Unset = UNSET
    radio: None | UIElementRadio | Unset = UNSET
    depends_on: list[FieldDependency] | None | Unset = UNSET
    disabled: bool | None | Unset = UNSET
    use_namespace_when_not_source_aligned: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ui_element_checkbox import UIElementCheckbox
        from ..models.ui_element_radio import UIElementRadio
        from ..models.ui_element_select import UIElementSelect
        from ..models.ui_element_string import UIElementString

        label = self.label

        type_ = self.type_.value

        required = self.required

        name = self.name

        tooltip: None | str | Unset
        if isinstance(self.tooltip, Unset):
            tooltip = UNSET
        else:
            tooltip = self.tooltip

        hidden: bool | None | Unset
        if isinstance(self.hidden, Unset):
            hidden = UNSET
        else:
            hidden = self.hidden

        checkbox: dict[str, Any] | None | Unset
        if isinstance(self.checkbox, Unset):
            checkbox = UNSET
        elif isinstance(self.checkbox, UIElementCheckbox):
            checkbox = self.checkbox.to_dict()
        else:
            checkbox = self.checkbox

        select: dict[str, Any] | None | Unset
        if isinstance(self.select, Unset):
            select = UNSET
        elif isinstance(self.select, UIElementSelect):
            select = self.select.to_dict()
        else:
            select = self.select

        string: dict[str, Any] | None | Unset
        if isinstance(self.string, Unset):
            string = UNSET
        elif isinstance(self.string, UIElementString):
            string = self.string.to_dict()
        else:
            string = self.string

        radio: dict[str, Any] | None | Unset
        if isinstance(self.radio, Unset):
            radio = UNSET
        elif isinstance(self.radio, UIElementRadio):
            radio = self.radio.to_dict()
        else:
            radio = self.radio

        depends_on: list[dict[str, Any]] | None | Unset
        if isinstance(self.depends_on, Unset):
            depends_on = UNSET
        elif isinstance(self.depends_on, list):
            depends_on = []
            for depends_on_type_0_item_data in self.depends_on:
                depends_on_type_0_item = depends_on_type_0_item_data.to_dict()
                depends_on.append(depends_on_type_0_item)

        else:
            depends_on = self.depends_on

        disabled: bool | None | Unset
        if isinstance(self.disabled, Unset):
            disabled = UNSET
        else:
            disabled = self.disabled

        use_namespace_when_not_source_aligned: bool | None | Unset
        if isinstance(self.use_namespace_when_not_source_aligned, Unset):
            use_namespace_when_not_source_aligned = UNSET
        else:
            use_namespace_when_not_source_aligned = (
                self.use_namespace_when_not_source_aligned
            )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "type": type_,
                "required": required,
                "name": name,
            }
        )
        if tooltip is not UNSET:
            field_dict["tooltip"] = tooltip
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if checkbox is not UNSET:
            field_dict["checkbox"] = checkbox
        if select is not UNSET:
            field_dict["select"] = select
        if string is not UNSET:
            field_dict["string"] = string
        if radio is not UNSET:
            field_dict["radio"] = radio
        if depends_on is not UNSET:
            field_dict["depends_on"] = depends_on
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if use_namespace_when_not_source_aligned is not UNSET:
            field_dict["use_namespace_when_not_source_aligned"] = (
                use_namespace_when_not_source_aligned
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_dependency import FieldDependency
        from ..models.ui_element_checkbox import UIElementCheckbox
        from ..models.ui_element_radio import UIElementRadio
        from ..models.ui_element_select import UIElementSelect
        from ..models.ui_element_string import UIElementString

        d = dict(src_dict)
        label = d.pop("label")

        type_ = UIElementType(d.pop("type"))

        required = d.pop("required")

        name = d.pop("name")

        def _parse_tooltip(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tooltip = _parse_tooltip(d.pop("tooltip", UNSET))

        def _parse_hidden(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        hidden = _parse_hidden(d.pop("hidden", UNSET))

        def _parse_checkbox(data: object) -> None | UIElementCheckbox | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                checkbox_type_0 = UIElementCheckbox.from_dict(data)

                return checkbox_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UIElementCheckbox | Unset, data)

        checkbox = _parse_checkbox(d.pop("checkbox", UNSET))

        def _parse_select(data: object) -> None | UIElementSelect | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                select_type_0 = UIElementSelect.from_dict(data)

                return select_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UIElementSelect | Unset, data)

        select = _parse_select(d.pop("select", UNSET))

        def _parse_string(data: object) -> None | UIElementString | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                string_type_0 = UIElementString.from_dict(data)

                return string_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UIElementString | Unset, data)

        string = _parse_string(d.pop("string", UNSET))

        def _parse_radio(data: object) -> None | UIElementRadio | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                radio_type_0 = UIElementRadio.from_dict(data)

                return radio_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UIElementRadio | Unset, data)

        radio = _parse_radio(d.pop("radio", UNSET))

        def _parse_depends_on(data: object) -> list[FieldDependency] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                depends_on_type_0 = []
                _depends_on_type_0 = data
                for depends_on_type_0_item_data in _depends_on_type_0:
                    depends_on_type_0_item = FieldDependency.from_dict(
                        depends_on_type_0_item_data
                    )

                    depends_on_type_0.append(depends_on_type_0_item)

                return depends_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[FieldDependency] | None | Unset, data)

        depends_on = _parse_depends_on(d.pop("depends_on", UNSET))

        def _parse_disabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        disabled = _parse_disabled(d.pop("disabled", UNSET))

        def _parse_use_namespace_when_not_source_aligned(
            data: object,
        ) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        use_namespace_when_not_source_aligned = (
            _parse_use_namespace_when_not_source_aligned(
                d.pop("use_namespace_when_not_source_aligned", UNSET)
            )
        )

        ui_element_metadata = cls(
            label=label,
            type_=type_,
            required=required,
            name=name,
            tooltip=tooltip,
            hidden=hidden,
            checkbox=checkbox,
            select=select,
            string=string,
            radio=radio,
            depends_on=depends_on,
            disabled=disabled,
            use_namespace_when_not_source_aligned=use_namespace_when_not_source_aligned,
        )

        ui_element_metadata.additional_properties = d
        return ui_element_metadata

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
