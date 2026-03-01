from app.shared.schema import ORMModel


class PostgreSQLConfig(ORMModel):
    database_name: str
