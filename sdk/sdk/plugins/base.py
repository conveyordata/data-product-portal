from typing import Any, ClassVar, Optional, Self

from pydantic import BaseModel


class TechnicalAssetConfiguration(BaseModel):
    """Typed configuration for a technical asset type the portal ships.

    The published API describes a configuration as a free-form object, because
    the portal cannot know the fields of a plugin installed from someone else's
    package. These models give the types back for the plugins we do ship. A
    third-party plugin supplies its own model, or passes a plain dict.
    """

    configuration_type: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "configuration_type": self.configuration_type,
            **self.model_dump(mode="json"),
        }

    @classmethod
    def from_configuration(cls, configuration: Any) -> Optional[Self]:
        """Read a configuration off a technical asset, or None for another type."""
        if getattr(configuration, "configuration_type", None) != cls.configuration_type:
            return None
        return cls.model_validate(configuration.to_dict())
