from enum import Enum


class UIElementType(str, Enum):
    String = "string"
    Select = "select"
    Checkbox = "checkbox"
    Radio = "radio"


class AccessGranularity(str, Enum):
    Schema = "schema"
    Table = "table"
