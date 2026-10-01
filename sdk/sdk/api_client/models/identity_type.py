from enum import Enum


class IdentityType(str, Enum):
    GROUP = "group"
    MACHINE_USER = "machine_user"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
