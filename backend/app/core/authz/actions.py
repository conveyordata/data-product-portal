from enum import UNIQUE, IntEnum, verify


@verify(UNIQUE)
class AuthorizationAction(IntEnum):
    """
    The integer values for the authorization actions are stored directly in the DB.
    This means you can change the name of the actions, but not their integer values.
    The values for the actions are spaced on purpose, to make it easier to extend.
    This has no technical benefit, but it makes it easier to read for developers.
    """

    GLOBAL__MODIFY_ROLES = 101

    DATAPRODUCT__CREATE = 301
    DATAPRODUCT__DELETE = 302
    DATAPRODUCT__UPDATE_DETAILS = 303
    DATAPRODUCT__UPDATE_STATUS = 304

    DATASET__CREATE = 401
    DATASET__DELETE = 402

    # TODO: add more actions
