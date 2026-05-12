from enum import Enum


class NodeType(str, Enum):
    DATAPRODUCTNODE = "dataProductNode"
    EXPLORATIONNODE = "explorationNode"
    OUTPUTPORTNODE = "outputPortNode"
    TECHNICALASSETNODE = "technicalAssetNode"

    def __str__(self) -> str:
        return str(self.value)
