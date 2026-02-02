from uuid import UUID

from app.data_products.output_ports.data_quality.schema_request import (
    OutputPortDataQualitySummary,
)


class OutputPortDataQualitySummaryResponse(OutputPortDataQualitySummary):
    id: UUID
    output_port_id: UUID
