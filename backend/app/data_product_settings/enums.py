from enum import Enum


class DataProductSettingType(str, Enum):
    CHECKBOX = "checkbox"
    TAGS = "tags"
    INPUT = "input"
