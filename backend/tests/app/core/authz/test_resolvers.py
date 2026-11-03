import asyncio
import json

import pytest
from fastapi import Request
from fastapi.routing import APIRoute
from pydantic import BaseModel

from app.core.authz.resolvers import DataProductResolver


class _DataProductPayload(BaseModel):
    data_product_id: str


def _query_or_path_endpoint(data_product_id: str): ...


def _model_body_endpoint(payload: _DataProductPayload): ...


def _no_key_endpoint(): ...


def _request(endpoint, path="/x", path_params=None, query="", body=b"") -> Request:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [],
        "query_string": query.encode(),
        "path_params": path_params or {},
        "route": APIRoute(path, endpoint),
    }
    return Request(scope, receive)


def _json(**values) -> bytes:
    return json.dumps(values).encode()


@pytest.mark.parametrize(
    ("http_request", "expected"),
    [
        pytest.param(
            _request(
                _query_or_path_endpoint,
                "/x/{data_product_id}",
                {"data_product_id": "target"},
                "data_product_id=allowed",
                _json(data_product_id="allowed"),
            ),
            "target",
            id="path ignores query and body",
        ),
        pytest.param(
            _request(
                _query_or_path_endpoint,
                query="data_product_id=target",
                body=_json(data_product_id="allowed"),
            ),
            "target",
            id="query ignores body",
        ),
        pytest.param(
            _request(
                _model_body_endpoint,
                query="data_product_id=allowed",
                body=_json(data_product_id="target"),
            ),
            "target",
            id="body ignores query",
        ),
        pytest.param(
            _request(
                _model_body_endpoint,
                "/x/{data_product_id}",
                {"data_product_id": "allowed"},
                body=_json(data_product_id="target"),
            ),
            "target",
            id="body ignores undeclared path placeholder",
        ),
        pytest.param(
            _request(_model_body_endpoint, body=_json(data_product_id=["allowed"])),
            "*",
            id="non-string value",
        ),
        pytest.param(
            _request(_model_body_endpoint, body=b"data_product_id=allowed"),
            "*",
            id="non-json body",
        ),
        pytest.param(
            _request(
                _no_key_endpoint,
                query="data_product_id=allowed",
                body=_json(data_product_id="allowed"),
            ),
            "*",
            id="undeclared key",
        ),
    ],
)
def test_resolve__reads_only_declared_location(http_request: Request, expected):
    resolved = asyncio.run(
        DataProductResolver._resolve(http_request, "data_product_id", None)
    )
    assert resolved == expected
