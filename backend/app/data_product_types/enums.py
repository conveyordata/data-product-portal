from enum import Enum


class DataProductIconKey(str, Enum):
    REPORTING = "reporting"
    PROCESSING = "processing"
    EXPLORATION = "exploration"
    INGESTION = "ingestion"
    MACHINE_LEARNING = "machine_learning"
    ANALYTICS = "analytics"
    DEFAULT = "default"
