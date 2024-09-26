import os

import requests
from fastapi import HTTPException, status

from app.core.auth.oidc import OIDCConfiguration


class NotebookBuilderConveyor:
    def __init__(self):
        self.api_key = os.getenv("CONVEYOR_API_KEY")
        self.api_secret = os.getenv("CONVEYOR_SECRET")
        self.conveyor_api = "https://app.conveyordata.com/api/v2"

        self.oidc = OIDCConfiguration(
            oidc_enabled=False,
            authority="https://auth.dataminded.cloud/oauth2",
            client_id=self.api_key,
            client_secret=self.api_secret,
            redirect_uri="https://app.conveyordata.com",
        )
        self.token = ""

    def authenticate(self) -> str:
        try:
            session = requests.Session()
            session.auth = (self.oidc.client_id, self.oidc.client_secret)
        except AttributeError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Please contact us on how to integrate with Conveyor",
            )
        result = session.post(
            "https://auth.dataminded.cloud/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.oidc.client_id,
                "client_secret": self.oidc.client_secret,
            },
        )
        return result.json().get("access_token")

    def test_and_reauth(self) -> None:
        result = requests.get(
            f"{self.conveyor_api}/environments",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if result.status_code != 200:
            self.token = self.authenticate()
        result = requests.get(
            f"{self.conveyor_api}/environments",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if result.status_code != 200:
            raise ValueError("still unauthenticated with conveyor after reauth attempt")

    def get_conveyor_data_product_id(self, data_product: str) -> str:
        self.test_and_reauth()

        data_products = requests.get(
            f"{self.conveyor_api}/projects",
            headers={"Authorization": f"Bearer {self.token}"},
        ).json()
        try:
            data_product_id = next(
                (
                    p.get("id")
                    for p in data_products.get("projects")
                    if p.get("name") == data_product
                ),
                None,
            )
            if not data_product_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"data product {data_product} not found in Conveyor",
                )
        except TypeError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"data product {data_product} not found in Conveyor",
            )
        return data_product_id

    def generate_notebook_url(self, data_product: str) -> str:
        data_product_id = self.get_conveyor_data_product_id(data_product)
        url = f"https://app.conveyordata.com/projects/{data_product_id}/notebooks"
        return url

    def generate_ide_url(self, data_product: str) -> str:
        data_product_id = self.get_conveyor_data_product_id(data_product)
        url = f"https://app.conveyordata.com/projects/{data_product_id}/executions"
        return url


CONVEYOR_SERVICE = NotebookBuilderConveyor()
