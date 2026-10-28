from enum import UNIQUE, StrEnum, verify


@verify(UNIQUE)
class IdentityType(StrEnum):
    USER = "user"
    GROUP = "group"
    MACHINE_USER = "machine_user"
