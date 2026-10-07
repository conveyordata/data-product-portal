from enum import StrEnum


class DataProductSettingScope(StrEnum):
    DATAPRODUCT = "dataproduct"
    DATASET = "dataset"

    def __str__(self) -> str:
        return str(self.value)
