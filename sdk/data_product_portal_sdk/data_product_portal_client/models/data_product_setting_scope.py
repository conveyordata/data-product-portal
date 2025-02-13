from enum import Enum


class DataProductSettingScope(str, Enum):
    DATAPRODUCT = "dataproduct"
    DATASET = "dataset"

    def __str__(self) -> str:
        return str(self.value)
