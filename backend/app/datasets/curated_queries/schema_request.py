from app.shared.schema import ORMModel


class DatasetCuratedQueryInput(ORMModel):
    title: str
    description: str | None = None
    query_text: str
    sort_order: int | None = None


class DatasetCuratedQueriesUpdate(ORMModel):
    curated_queries: list[DatasetCuratedQueryInput]
