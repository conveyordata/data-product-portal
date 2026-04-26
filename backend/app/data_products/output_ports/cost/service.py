from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.data_products.output_ports.cost.model import OutputPortCostRecord
from app.data_products.output_ports.cost.schema_request import CreateCostRecord
from app.data_products.output_ports.model import Dataset, ensure_output_port_exists


class OutputPortCostService:
    def __init__(self, db: Session):
        self.db = db

    def push_cost_record(
        self, output_port_id: UUID, record: CreateCostRecord
    ) -> OutputPortCostRecord:
        ensure_output_port_exists(output_port_id, self.db)
        recorded_at = record.recorded_at or date.today()
        db_record = OutputPortCostRecord(
            output_port_id=output_port_id,
            recorded_at=recorded_at,
            compute_cost=record.compute_cost,
            storage_cost=record.storage_cost,
            platform_overhead_cost=record.platform_overhead_cost,
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def get_cost_history(
        self, output_port_id: UUID, day_range: int = 90
    ) -> list[OutputPortCostRecord]:
        ensure_output_port_exists(output_port_id, self.db)
        start_date = date.today() - timedelta(days=day_range)
        return (
            self.db.query(OutputPortCostRecord)
            .filter(
                OutputPortCostRecord.output_port_id == output_port_id,
                OutputPortCostRecord.recorded_at >= start_date,
            )
            .order_by(OutputPortCostRecord.recorded_at.desc())
            .all()
        )

    def get_data_product_cost_summary(
        self, data_product_id: UUID, day_range: int = 30
    ) -> list:
        start_date = date.today() - timedelta(days=day_range)
        return (
            self.db.query(
                OutputPortCostRecord.output_port_id,
                Dataset.name.label("output_port_name"),
                func.sum(OutputPortCostRecord.compute_cost).label("compute_cost"),
                func.sum(OutputPortCostRecord.storage_cost).label("storage_cost"),
                func.sum(OutputPortCostRecord.platform_overhead_cost).label(
                    "platform_overhead_cost"
                ),
            )
            .join(Dataset, Dataset.id == OutputPortCostRecord.output_port_id)
            .filter(
                Dataset.data_product_id == data_product_id,
                OutputPortCostRecord.recorded_at >= start_date,
            )
            .group_by(OutputPortCostRecord.output_port_id, Dataset.name)
            .all()
        )
