from typing import Optional

from app.shared.schema import ORMModel


class OutputPortCuratedQueryInput(ORMModel):
    title: str
    description: Optional[str] = None
    query_text: str


class OutputPortCuratedQueriesUpdate(ORMModel):
    curated_queries: list[OutputPortCuratedQueryInput]
