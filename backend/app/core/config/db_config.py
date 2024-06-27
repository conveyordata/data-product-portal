import os


class DBConfig:
    def __init__(self):
        self.password = self.get_db_config("POSTGRES_PASSWORD")
        self.user = self.get_db_config("POSTGRES_USER")
        self.name = self.get_db_config("POSTGRES_DB")
        self.port = self.get_db_config("POSTGRES_PORT")
        self.server = self.get_db_config("POSTGRES_SERVER")

    def get_db_config(self, config: str) -> str:
        value = os.getenv(config)
        if not value:
            raise ValueError(
                f"{config} must be explicitly set to a value for DB configuration"
            )
        return value
