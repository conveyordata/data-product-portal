from typing import Sequence
from uuid import UUID

from sqlalchemy import asc, delete, select
from sqlalchemy.orm import Session

from app.datasets.curated_queries.model import (
    DatasetCuratedQuery as DatasetCuratedQueryModel,
)
from app.datasets.curated_queries.schema_request import DatasetCuratedQueryInput
from app.datasets.model import ensure_dataset_exists


class DatasetCuratedQueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_curated_queries(
        self, dataset_id: UUID
    ) -> Sequence[DatasetCuratedQueryModel]:
        ensure_dataset_exists(dataset_id, self.db)
        return self.db.scalars(
            select(DatasetCuratedQueryModel)
            .where(DatasetCuratedQueryModel.output_port_id == dataset_id)
            .order_by(
                asc(DatasetCuratedQueryModel.sort_order),
                asc(DatasetCuratedQueryModel.created_at),
            )
        ).all()

    def replace_curated_queries(
        self, dataset_id: UUID, curated_queries: Sequence[DatasetCuratedQueryInput]
    ) -> Sequence[DatasetCuratedQueryModel]:
        ensure_dataset_exists(dataset_id, self.db)
        self.db.execute(
            delete(DatasetCuratedQueryModel).where(
                DatasetCuratedQueryModel.output_port_id == dataset_id
            )
        )
        for index, curated_query in enumerate(curated_queries):
            self.db.add(
                DatasetCuratedQueryModel(
                    output_port_id=dataset_id,
                    title=curated_query.title,
                    description=curated_query.description,
                    query_text=curated_query.query_text,
                    sort_order=curated_query.sort_order
                    if curated_query.sort_order is not None
                    else index,
                )
            )
        self.db.commit()
        return self.get_curated_queries(dataset_id)
