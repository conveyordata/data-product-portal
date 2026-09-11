"""The base class a technical asset plugin inherits from (ADR-0024).

A plugin depends on the SDK, not the portal itself - the portal loads
plugin classes by entry point, never by importing the portal into the
plugin's own process.
"""

from abc import ABC, abstractmethod
from importlib import resources
from typing import Any, ClassVar, TypedDict


class PluginField(TypedDict, total=False):
    """A plugin's own, deliberately minimal field descriptor (ADR-0024).

    For now, every field is a string; `pattern` (a regex, checked both
    client- and server-side) covers most of what a field actually needs
    to validate.
    """

    name: str
    label: str
    required: bool
    type: str  # Only "string" is currently rendered by the portal's adapter.
    pattern: str
    tooltip: str


class TechnicalAssetPlugin(ABC):
    key: ClassVar[str]
    display_name: ClassVar[str]
    icon_package: ClassVar[str]
    icon_resource: ClassVar[str]
    fields: ClassVar[list[PluginField]]

    target_revision: ClassVar[str]
    migrations_package: ClassVar[str]

    # Whether this plugin participates in the portal's existing environment
    # model (`Environment`, e.g. development/production) - if True, the
    # access-tile UI shows an environment picker, and `get_url`'s context
    # carries the resolved `Environment.context` and the data product's
    # namespace, the same information a built-in type's `get_url` already
    # receives.
    has_environments: ClassVar[bool] = False

    # The plugin's own SQLAlchemy model for its owned table - the portal
    # uses this to persist/read values, never through its own ORM.
    model: ClassVar[Any]

    REQUIRED_ATTRS: ClassVar[tuple[str, ...]] = (
        "key",
        "display_name",
        "icon_package",
        "icon_resource",
        "fields",
        "target_revision",
        "migrations_package",
        "model",
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        missing = [attr for attr in cls.REQUIRED_ATTRS if not hasattr(cls, attr)]
        if missing:
            raise TypeError(f"{cls.__name__} is missing required attributes: {missing}")

    @classmethod
    def get_icon(cls) -> bytes:
        return (
            resources.files(cls.icon_package).joinpath(cls.icon_resource).read_bytes()
        )

    @classmethod
    @abstractmethod
    def validate(cls, values: dict[str, Any], context: Any) -> None: ...

    @classmethod
    @abstractmethod
    def render_result(cls, values: dict[str, Any], context: Any) -> str: ...

    @classmethod
    @abstractmethod
    def get_url(cls, values: dict[str, Any], context: Any) -> str: ...
