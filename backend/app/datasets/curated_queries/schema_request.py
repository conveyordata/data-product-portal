from typing import Optional

from app.shared.schema import ORMModel


class DatasetCuratedQueryInput(ORMModel):
    title: str
    description: Optional[str] = None
    query_text: str


class DatasetCuratedQueriesUpdate(ORMModel):
    curated_queries: list[DatasetCuratedQueryInput]
