from enum import StrEnum


class NodeType(StrEnum):
    DATAPRODUCTNODE = "dataProductNode"
    EXPLORATIONNODE = "explorationNode"
    OUTPUTPORTNODE = "outputPortNode"
    TECHNICALASSETNODE = "technicalAssetNode"

    def __str__(self) -> str:
        return str(self.value)
