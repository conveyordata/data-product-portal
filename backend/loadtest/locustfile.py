import os

from locust import HttpUser, between, task

DATA_PRODUCTS_PATH = os.getenv("LOADTEST_DATA_PRODUCTS_PATH", "/api/v2/data_products")
SEARCH_OUTPUT_PORTS_PATH = os.getenv(
    "LOADTEST_SEARCH_OUTPUT_PORTS_PATH", "/api/v2/search/output_ports"
)
SEARCH_QUERY = os.getenv("LOADTEST_SEARCH_QUERY", "data")
WAIT_TIME_MIN_SECONDS = float(os.getenv("LOADTEST_WAIT_TIME_MIN_SECONDS", "0.2"))
WAIT_TIME_MAX_SECONDS = float(os.getenv("LOADTEST_WAIT_TIME_MAX_SECONDS", "1.0"))
DATA_PRODUCTS_WEIGHT = int(os.getenv("LOADTEST_DATA_PRODUCTS_WEIGHT", "70"))
SEARCH_OUTPUT_PORTS_WEIGHT = int(os.getenv("LOADTEST_SEARCH_OUTPUT_PORTS_WEIGHT", "30"))

if DATA_PRODUCTS_WEIGHT < 0 or SEARCH_OUTPUT_PORTS_WEIGHT < 0:
    raise ValueError("Endpoint weights must be >= 0")
if DATA_PRODUCTS_WEIGHT + SEARCH_OUTPUT_PORTS_WEIGHT == 0:
    raise ValueError("At least one endpoint weight must be > 0")


class PortalReadUser(HttpUser):
    wait_time = between(WAIT_TIME_MIN_SECONDS, WAIT_TIME_MAX_SECONDS)

    def on_start(self) -> None:
        self._headers: dict[str, str] = {}

        bearer_token = os.getenv("LOADTEST_BEARER_TOKEN")
        if bearer_token:
            self._headers["Authorization"] = f"Bearer {bearer_token}"

        header_name = os.getenv("LOADTEST_AUTH_HEADER_NAME")
        header_value = os.getenv("LOADTEST_AUTH_HEADER_VALUE")
        if header_name and header_value:
            self._headers[header_name] = header_value

    @task(DATA_PRODUCTS_WEIGHT)
    def get_data_products(self) -> None:
        self.client.get(
            DATA_PRODUCTS_PATH,
            headers=self._headers,
            name="GET /api/v2/data_products",
        )

    @task(SEARCH_OUTPUT_PORTS_WEIGHT)
    def search_output_ports(self) -> None:
        self.client.get(
            SEARCH_OUTPUT_PORTS_PATH,
            params={"query": SEARCH_QUERY},
            headers=self._headers,
            name="GET /api/v2/search/output_ports",
        )
