from typing import Sequence

from typing_extensions import deprecated

from app.data_products.output_ports.schema_response import DatasetsGet, OutputPortsGet
from app.shared.schema import ORMModel


class SearchOutputPortsResponseItem(OutputPortsGet):
    pass


@deprecated("Use SearchOutputPortsResponseItem instead")
class SearchDatasets(DatasetsGet):
    pass

    def convert(self):
        return SearchOutputPortsResponseItem(
            **self.model_dump(
                exclude={
                    "data_output_links",
                    "data_product_settings",
                }
            ),
            technical_asset_links=[dol.convert() for dol in self.data_output_links],
            data_product_settings=[s.convert() for s in self.data_product_settings],
        )


class SearchOutputPortsResponse(ORMModel):
    output_ports: Sequence[SearchOutputPortsResponseItem]
