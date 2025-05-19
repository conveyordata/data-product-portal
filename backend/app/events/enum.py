from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class EventReferenceEntity(str, Enum):
    DATA_PRODUCT = "data_product"
    DATASET = "dataset"
    DATA_OUTPUT = "data_output"
    USER = "user"
