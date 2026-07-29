import asyncio as _asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from app.core.auth.credentials import AWSCredentials
from app.technical_asset_configuration.glue.mcp_tools import _fetch_aws_credentials
from tests.factories import UserFactory


@pytest.fixture
def user(session):
    return UserFactory()


@pytest.fixture
def mock_creds():
    from datetime import datetime, timezone

    return AWSCredentials(
        AccessKeyId="AKIA...",
        SecretAccessKey="secret",
        SessionToken="token",
        Expiration=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )


class TestFetchAwsCredentials:
    def test_raises_tool_error_on_permission_denied(self, session, user):
        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.authorize_data_product_read_integrations",
                side_effect=PermissionError("no access"),
            ),
            pytest.raises(ToolError, match="no access"),
        ):
            _fetch_aws_credentials("my-product", "prod", user, session)

    def test_raises_tool_error_on_invalid_namespace(self, session, user):
        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.authorize_data_product_read_integrations",
                side_effect=ValueError("unknown namespace"),
            ),
            pytest.raises(ToolError, match="unknown namespace"),
        ):
            _fetch_aws_credentials("unknown", "prod", user, session)

    def test_raises_tool_error_when_auth_service_fails(self, session, user):
        mock_env = MagicMock()
        mock_env.name = "prod"
        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.authorize_data_product_read_integrations"
            ),
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.EnvironmentService.get_environments",
                return_value=[mock_env],
            ),
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.AuthService.get_aws_credentials",
                side_effect=Exception("STS error"),
            ),
            pytest.raises(ToolError, match="STS error"),
        ):
            _fetch_aws_credentials("my-product", "prod", user, session)

    def test_returns_credentials_on_success(self, session, user, mock_creds):
        mock_env = MagicMock()
        mock_env.name = "prod"
        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.authorize_data_product_read_integrations"
            ),
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.EnvironmentService.get_environments",
                return_value=[mock_env],
            ),
            patch(
                "app.technical_asset_configuration.glue.mcp_tools.AuthService.get_aws_credentials",
                return_value=mock_creds,
            ),
        ):
            result = _fetch_aws_credentials("my-product", "prod", user, session)

        assert result.AccessKeyId == "AKIA..."
        assert result.SessionToken == "token"


class TestListGlueTables:
    def test_returns_tables_from_paginator(self, session, user, mock_creds):
        fake_page = {
            "TableList": [
                {"Name": "orders", "TableType": "EXTERNAL_TABLE"},
                {"Name": "customers", "TableType": "EXTERNAL_TABLE"},
            ]
        }
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [fake_page]
        mock_client = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_list_glue_tables(
                data_product_namespace="my-product",
                env="prod",
                database_name="mydb",
                authorized_user=user,
                db=session,
            )

        assert result["table_count"] == 2
        assert "orders" in result["table_names"]
        assert "customers" in result["table_names"]

    def test_raises_tool_error_for_missing_database(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = (
            mock_client.exceptions.EntityNotFoundException()
        )
        mock_client.get_paginator.return_value = mock_paginator
        mock_client.exceptions.EntityNotFoundException = type(
            "EntityNotFoundException", (Exception,), {}
        )
        mock_paginator.paginate.side_effect = (
            mock_client.exceptions.EntityNotFoundException()
        )

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
            pytest.raises(ToolError, match="not found in Glue catalog"),
        ):
            _call_list_glue_tables(
                data_product_namespace="my-product",
                env="prod",
                database_name="missing_db",
                authorized_user=user,
                db=session,
            )


class TestQueryAthena:
    def test_returns_execution_id_on_success(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.start_query_execution.return_value = {"QueryExecutionId": "qry-123"}

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_query_athena(
                data_product_namespace="my-product",
                env="prod",
                query="SELECT 1",
                authorized_user=user,
                db=session,
            )

        assert result["query_execution_id"] == "qry-123"
        assert result["data_product_namespace"] == "my-product"

    def test_passes_workgroup_when_provided(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.start_query_execution.return_value = {"QueryExecutionId": "qry-456"}

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_query_athena(
                data_product_namespace="my-product",
                env="prod",
                query="SELECT 1",
                workgroup="my-workgroup",
                authorized_user=user,
                db=session,
            )

        call_kwargs = mock_client.start_query_execution.call_args[1]
        assert call_kwargs["WorkGroup"] == "my-workgroup"
        assert result["workgroup"] == "my-workgroup"

    def test_raises_tool_error_on_invalid_query(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.exceptions.InvalidRequestException = type(
            "InvalidRequestException", (Exception,), {}
        )
        mock_client.start_query_execution.side_effect = (
            mock_client.exceptions.InvalidRequestException("bad SQL")
        )

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
            pytest.raises(ToolError, match="Invalid Athena query"),
        ):
            _call_query_athena(
                data_product_namespace="my-product",
                env="prod",
                query="SELECT ??? INVALID",
                authorized_user=user,
                db=session,
            )


class TestGetAthenaQueryResults:
    def _make_execution(self, state, rows=None, error=None):
        execution = {
            "QueryExecution": {
                "Status": {"State": state},
                "Statistics": {
                    "DataScannedInBytes": 1024,
                    "EngineExecutionTimeInMillis": 500,
                },
            }
        }
        if error:
            execution["QueryExecution"]["Status"]["StateChangeReason"] = error
        return execution

    def test_returns_running_status(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.get_query_execution.return_value = self._make_execution("RUNNING")

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_get_athena_query_results(
                query_execution_id="qry-123",
                data_product_namespace="my-product",
                env="prod",
                authorized_user=user,
                db=session,
            )

        assert result["status"] == "RUNNING"
        assert "Retry" in result["message"]

    def test_raises_tool_error_on_failed_query(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.get_query_execution.return_value = self._make_execution(
            "FAILED", error="Syntax error in SQL"
        )

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
            pytest.raises(ToolError, match="Syntax error in SQL"),
        ):
            _call_get_athena_query_results(
                query_execution_id="qry-123",
                data_product_namespace="my-product",
                env="prod",
                authorized_user=user,
                db=session,
            )

    def test_returns_rows_on_success(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.get_query_execution.return_value = self._make_execution("SUCCEEDED")
        mock_client.get_query_results.return_value = {
            "ResultSet": {
                "Rows": [
                    {"Data": [{"VarCharValue": "id"}, {"VarCharValue": "name"}]},
                    {"Data": [{"VarCharValue": "1"}, {"VarCharValue": "Alice"}]},
                    {"Data": [{"VarCharValue": "2"}, {"VarCharValue": "Bob"}]},
                ]
            }
        }

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_get_athena_query_results(
                query_execution_id="qry-123",
                data_product_namespace="my-product",
                env="prod",
                authorized_user=user,
                db=session,
            )

        assert result["status"] == "SUCCEEDED"
        assert result["row_count"] == 2
        assert result["columns"] == ["id", "name"]
        assert result["rows"][0] == {"id": "1", "name": "Alice"}

    def test_returns_empty_rows_when_no_results(self, session, user, mock_creds):
        mock_client = MagicMock()
        mock_client.get_query_execution.return_value = self._make_execution("SUCCEEDED")
        mock_client.get_query_results.return_value = {"ResultSet": {"Rows": []}}

        with (
            patch(
                "app.technical_asset_configuration.glue.mcp_tools._fetch_aws_credentials",
                return_value=mock_creds,
            ),
            patch("boto3.client", return_value=mock_client),
        ):
            result = _call_get_athena_query_results(
                query_execution_id="qry-123",
                data_product_namespace="my-product",
                env="prod",
                authorized_user=user,
                db=session,
            )

        assert result["row_count"] == 0
        assert result["rows"] == []


_TOOLS = None


def _get_tools():
    global _TOOLS
    if _TOOLS is None:
        _TOOLS = {}
        from fastmcp import FastMCP

        from app.technical_asset_configuration.glue.mcp_tools import register_tools

        mcp = FastMCP()
        register_tools(mcp)
        for t in _asyncio.run(mcp.list_tools()):
            tool_obj = _asyncio.run(mcp.get_tool(t.name))
            _TOOLS[t.name] = tool_obj.fn
    return _TOOLS


def _call_list_glue_tables(**kwargs):
    return _get_tools()["list_glue_tables"](**kwargs)


def _call_query_athena(**kwargs):
    return _get_tools()["query_athena"](**kwargs)


def _call_get_athena_query_results(**kwargs):
    return _get_tools()["get_athena_query_results"](**kwargs)
