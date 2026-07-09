class DataProductPortalException(Exception):
    pass


class NotFoundInDB(DataProductPortalException):
    pass


class InvalidInputPortState(DataProductPortalException):
    pass
