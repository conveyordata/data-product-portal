from enum import StrEnum


class PlatformTypeKind(StrEnum):
    ASSET = "asset"
    TOOL = "tool"

    def __str__(self) -> str:
        return str(self.value)
