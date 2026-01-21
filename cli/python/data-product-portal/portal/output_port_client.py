import requests
from typing import Dict, Any
from portal.auth.auth import PortalAuth


class OutputPortClient:
    """
    Thin HTTP client for interacting with Output Port APIs.

    Authentication is delegated to an auth provider that exposes:
      - get_access_token() -> str
      - base_url (str)
    """

    def __init__(
        self,
        auth_provider: PortalAuth = PortalAuth(),
        timeout: int = 10,
    ):
        self.timeout = timeout
        self.auth_provider = auth_provider
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_provider.get_access_token()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def post_data_quality_summary(
        self,
        product_id: str,
        output_port_id: str,
        summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        url = (
            f"{self.auth_provider.base_url}"
            f"/v2/data_products/{product_id}"
            f"/output_ports/{output_port_id}"
            f"/data_quality_summary"
        )
        print(f"Posting data quality summary to {url}")
        print(summary)

        response = self.session.post(
            url,
            json=summary,
            timeout=self.timeout,
        )

        if not response.ok:
            raise RuntimeError(
                f"Failed to post data quality summary "
                f"(status={response.status_code}): {response.text}"
            )
        else:
            print(f"Successfully posted data quality summary: {summary}")
            return summary
