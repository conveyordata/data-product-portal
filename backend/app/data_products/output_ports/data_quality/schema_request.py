from datetime import datetime
from typing import Dict, Optional, Sequence

from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.shared.schema import ORMModel


class DataQualityTechnicalAsset(ORMModel):
    name: str
    status: DataQualityStatus


class OutputPortDataQualitySummary(ORMModel):
    created_at: datetime
    overall_status: DataQualityStatus
    description: Optional[str] = None
    details_url: Optional[str] = None
    technical_assets: Sequence[DataQualityTechnicalAsset]
    dimensions: Optional[Dict[str, DataQualityStatus]] = None
