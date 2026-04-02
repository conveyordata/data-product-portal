from enum import Enum


class NodeType(str, Enum):
    DATAOUTPUTNODE = "dataOutputNode"
    DATAPRODUCTNODE = "dataProductNode"
    DATASETNODE = "datasetNode"
    DOMAINNODE = "domainNode"

    def __str__(self) -> str:
        return str(self.value)
