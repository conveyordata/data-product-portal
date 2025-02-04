from enum import UNIQUE, StrEnum, auto, verify


@verify(UNIQUE)
class AuthorizedAction(StrEnum):
    DATAPRODUCT__CREATE = auto()
    DATAPRODUCT__DELETE = auto()
    DATAPRODUCT__UPDATE_DETAILS = auto()
    DATAPRODUCT__UPDATE_STATUS = auto()

    # TODO: add more actions
