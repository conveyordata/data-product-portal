from enum import Enum


class DataProductIconKey(str, Enum):
    ANALYTICS = "analytics"
    DEFAULT = "default"
    EXPLORATION = "exploration"
    INGESTION = "ingestion"
    MACHINE_LEARNING = "machine_learning"
    PROCESSING = "processing"
    REPORTING = "reporting"

    def __str__(self) -> str:
        return str(self.value)
