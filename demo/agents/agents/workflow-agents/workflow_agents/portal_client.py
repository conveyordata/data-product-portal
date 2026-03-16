"""Portal REST client shared across all workflows."""

from __future__ import annotations

import os
from typing import Any

import httpx

_PORTAL_API_URL = os.environ.get("PORTAL_API_URL", "http://backend:5050")
_PORTAL_ADMIN_USER = os.environ.get("PORTAL_ADMIN_USER", "")
_PORTAL_ADMIN_PASSWORD = os.environ.get("PORTAL_ADMIN_PASSWORD", "")


class PortalClient:
    """Thin wrapper around the Portal REST API using httpx."""

    def __init__(self) -> None:
        # In sandbox mode (OIDC_ENABLED=false) no credentials are required.
        # Auth headers are set only when explicitly configured.
        headers: dict[str, str] = {}
        if _PORTAL_ADMIN_USER and _PORTAL_ADMIN_PASSWORD:
            import base64

            creds = base64.b64encode(
                f"{_PORTAL_ADMIN_USER}:{_PORTAL_ADMIN_PASSWORD}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {creds}"

        self._client = httpx.Client(
            base_url=_PORTAL_API_URL,
            headers=headers,
            timeout=30.0,
        )

    def get_domains(self) -> list[dict[str, Any]]:
        resp = self._client.get("/api/v2/configuration/domains")
        resp.raise_for_status()
        return resp.json().get("domains", [])

    def get_data_product_types(self) -> list[dict[str, Any]]:
        resp = self._client.get("/api/v2/configuration/data_product_types")
        resp.raise_for_status()
        return resp.json().get("data_product_types", [])

    def get_lifecycles(self) -> list[dict[str, Any]]:
        resp = self._client.get("/api/v2/configuration/data_product_lifecycles")
        resp.raise_for_status()
        return resp.json().get("data_product_life_cycles", [])

    def get_current_user(self) -> dict[str, Any]:
        """Return the first user matching DEFAULT_USERNAME, or any user as fallback."""
        default_email = os.environ.get("DEFAULT_USERNAME", "")
        resp = self._client.get("/api/v2/users")
        resp.raise_for_status()
        users = resp.json().get("users", [])
        if not users:
            raise RuntimeError("No users found in Portal")
        if default_email:
            for u in users:
                if u.get("email", "").lower() == default_email.lower():
                    return u
        return users[0]

    def search_data_products(self, query: str) -> list[dict[str, Any]]:
        resp = self._client.get("/api/v2/data_products")
        resp.raise_for_status()
        products = resp.json().get("data_products", [])
        if not query:
            return products
        q = query.lower()
        return [
            p
            for p in products
            if q in (p.get("name") or "").lower()
            or q in (p.get("description") or "").lower()
        ]

    def create_data_product(
        self,
        name: str,
        namespace: str,
        description: str,
        domain_id: str,
        type_id: str,
        lifecycle_id: str,
        owner_id: str,
        about: str = "",
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "namespace": namespace,
            "description": description,
            "domain_id": domain_id,
            "type_id": type_id,
            "lifecycle_id": lifecycle_id,
            "about": about,
            "tag_ids": [],
            "owners": [owner_id],
        }
        resp = self._client.post("/api/v2/data_products", json=payload)
        resp.raise_for_status()
        return resp.json()

    def search_output_ports(self, query: str) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if query and len(query) >= 3:
            params["query"] = query
        resp = self._client.get("/api/v2/search/output_ports", params=params)
        resp.raise_for_status()
        return resp.json().get("output_ports", [])

    def get_output_port(self, dataset_id: str) -> dict[str, Any]:
        resp = self._client.get(f"/api/v2/datasets/{dataset_id}")
        resp.raise_for_status()
        return resp.json()

    def request_output_port_access(
        self,
        consumer_data_product_id: str,
        dataset_ids: list[str],
        justification: str,
    ) -> dict[str, Any]:
        """Link output ports to the consumer data product (requesting access)."""
        payload = {
            "input_ports": dataset_ids,
            "justification": justification,
        }
        resp = self._client.post(
            f"/api/v2/data_products/{consumer_data_product_id}/link_input_ports",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    def get_input_ports(self, consumer_data_product_id: str) -> list[dict[str, Any]]:
        """Return input port links for the consumer data product."""
        resp = self._client.get(
            f"/api/v2/data_products/{consumer_data_product_id}/input_ports"
        )
        resp.raise_for_status()
        return resp.json().get("input_ports", [])

    def create_ephemeral_access(
        self,
        output_port_ids: list[str],
        ttl_hours: int = 8,
        justification: str = "",
    ) -> dict[str, Any]:
        """Create an ephemeral data product for ad-hoc access. Returns {"id": "<uuid>"}."""
        payload = {
            "output_port_ids": output_port_ids,
            "ttl_hours": ttl_hours,
            "justification": justification,
        }
        resp = self._client.post("/api/v2/ephemeral_access", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_data_product(self, data_product_id: str) -> dict[str, Any]:
        """Fetch a data product by id. Returns full DP with namespace, is_ephemeral, etc."""
        resp = self._client.get(f"/api/v2/data_products/{data_product_id}")
        resp.raise_for_status()
        return resp.json()
