from enum import Enum


class SemanticModelFormat(str, Enum):
    METRICSFLOW = "MetricsFlow"
    OPENSEMANTICINTERCHANGE = "OpenSemanticInterchange"

    def __str__(self) -> str:
        return str(self.value)
