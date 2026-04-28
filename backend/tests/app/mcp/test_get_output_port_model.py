# ruff: noqa: S106
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

OUTPUT_PORT_ID = "aaaaaaaa-0000-0000-0000-000000000001"


class TestGetOutputPortModel:
    def test_returns_output_port_metadata_with_table_schemas_and_column_tags(self):
        """Core compliance use case: output port metadata + columns with PII tags."""
        mock_db = MagicMock()
        mock_token = MagicMock(token="test-token")
        mock_user = {"id": str(uuid4()), "email": "user@example.com"}

        mock_dataset = MagicMock()
        mock_dataset.id = UUID(OUTPUT_PORT_ID)
        mock_dataset.name = "Customer Profiles"
        mock_dataset.description = "Core customer data"
        mock_dataset.about = "This dataset contains personal data subject to GDPR."
        mock_dataset.access_type = MagicMock(value="restricted")
        mock_dataset.tags = []

        mock_schema = MagicMock()
        mock_schema_dict = {
            "id": str(uuid4()),
            "output_port_id": OUTPUT_PORT_ID,
            "name": "customers",
            "description": None,
            "tags": [],
            "columns": [
                {
                    "id": str(uuid4()),
                    "name": "email",
                    "description": "Customer email address",
                    "data_type": "string",
                    "tags": [{"id": str(uuid4()), "value": "PII"}],
                },
                {
                    "id": str(uuid4()),
                    "name": "customer_id",
                    "description": "Unique identifier",
                    "data_type": "uuid",
                    "tags": [],
                },
            ],
        }
        mock_schema_response = MagicMock()
        mock_schema_response.model_dump.return_value = mock_schema_dict

        mock_op_service = MagicMock()
        mock_op_service.get_dataset.return_value = mock_dataset

        mock_ts_service = MagicMock()
        mock_ts_service.get_all.return_value = [mock_schema]

        mock_sm_service = MagicMock()
        mock_sm_service.get_all.return_value = []

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
            patch("app.mcp.mcp.TableSchemaService", return_value=mock_ts_service),
            patch("app.mcp.mcp.SemanticModelService", return_value=mock_sm_service),
            patch("app.mcp.mcp.TableSchemaResponse") as mock_ts_cls,
            patch("app.mcp.mcp.SemanticModelResponse"),
        ):
            mock_ts_cls.model_validate.return_value = mock_schema_response
            from app.mcp.mcp import get_output_port_model

            result = get_output_port_model(output_port_id=OUTPUT_PORT_ID)

        assert "error" not in result
        assert result["output_port"]["name"] == "Customer Profiles"
        assert (
            result["output_port"]["about"]
            == "This dataset contains personal data subject to GDPR."
        )
        assert result["output_port"]["access_type"] == "restricted"
        assert result["output_port"]["tags"] == []
        assert len(result["table_schemas"]) == 1
        pii_col = result["table_schemas"][0]["columns"][0]
        assert pii_col["name"] == "email"
        assert pii_col["tags"][0]["value"] == "PII"
        assert result["semantic_models"] == []

    def test_returns_semantic_models(self):
        """Semantic model definitions are included in the response."""
        mock_db = MagicMock()
        mock_token = MagicMock(token="test-token")
        mock_user = {"id": str(uuid4()), "email": "user@example.com"}

        mock_dataset = MagicMock()
        mock_dataset.id = UUID(OUTPUT_PORT_ID)
        mock_dataset.name = "Audience Segments"
        mock_dataset.description = "Segmentation data"
        mock_dataset.about = None
        mock_dataset.access_type = MagicMock(value="public")
        mock_dataset.tags = []

        mock_sm = MagicMock()
        mock_sm_dict = {
            "id": str(uuid4()),
            "output_port_id": OUTPUT_PORT_ID,
            "name": "audience_segments",
            "format": "MetricsFlow",
            "content": {
                "semantic_models": [
                    {
                        "name": "audience_segments",
                        "entities": [
                            {
                                "name": "customer",
                                "type": "primary",
                                "expr": "customer_id",
                            }
                        ],
                        "measures": [
                            {
                                "name": "audience_size",
                                "agg": "count_distinct",
                                "expr": "customer_id",
                            }
                        ],
                        "dimensions": [],
                    }
                ],
                "metrics": [{"name": "audience_size", "type": "simple"}],
            },
        }
        mock_sm_response = MagicMock()
        mock_sm_response.model_dump.return_value = mock_sm_dict

        mock_op_service = MagicMock()
        mock_op_service.get_dataset.return_value = mock_dataset

        mock_ts_service = MagicMock()
        mock_ts_service.get_all.return_value = []

        mock_sm_service = MagicMock()
        mock_sm_service.get_all.return_value = [mock_sm]

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
            patch("app.mcp.mcp.TableSchemaService", return_value=mock_ts_service),
            patch("app.mcp.mcp.SemanticModelService", return_value=mock_sm_service),
            patch("app.mcp.mcp.TableSchemaResponse"),
            patch("app.mcp.mcp.SemanticModelResponse") as mock_sm_cls,
        ):
            mock_sm_cls.model_validate.return_value = mock_sm_response
            from app.mcp.mcp import get_output_port_model

            result = get_output_port_model(output_port_id=OUTPUT_PORT_ID)

        assert "error" not in result
        assert len(result["semantic_models"]) == 1
        sm = result["semantic_models"][0]
        assert sm["name"] == "audience_segments"
        assert sm["format"] == "MetricsFlow"
        assert "entities" in sm["content"]["semantic_models"][0]

    def test_output_port_not_found_returns_error(self):
        """Returns an error dict when the output port UUID does not exist."""
        mock_db = MagicMock()
        mock_token = MagicMock(token="test-token")
        mock_user = {"id": str(uuid4()), "email": "user@example.com"}

        mock_op_service = MagicMock()
        mock_op_service.get_dataset.return_value = None

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
        ):
            from app.mcp.mcp import get_output_port_model

            result = get_output_port_model(output_port_id=OUTPUT_PORT_ID)

        assert "error" in result
        assert OUTPUT_PORT_ID in result["error"]

    def test_output_port_tags_included(self):
        """Output-port-level tags (e.g. domain classification) are included."""
        mock_db = MagicMock()
        mock_token = MagicMock(token="test-token")
        mock_user = {"id": str(uuid4()), "email": "user@example.com"}

        tag_id = uuid4()
        mock_tag = MagicMock()
        mock_tag.id = tag_id
        mock_tag.value = "SENSITIVE"

        mock_dataset = MagicMock()
        mock_dataset.id = UUID(OUTPUT_PORT_ID)
        mock_dataset.name = "Financial Records"
        mock_dataset.description = "Finance data"
        mock_dataset.about = None
        mock_dataset.access_type = MagicMock(value="restricted")
        mock_dataset.tags = [mock_tag]

        mock_op_service = MagicMock()
        mock_op_service.get_dataset.return_value = mock_dataset

        mock_ts_service = MagicMock()
        mock_ts_service.get_all.return_value = []

        mock_sm_service = MagicMock()
        mock_sm_service.get_all.return_value = []

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
            patch("app.mcp.mcp.TableSchemaService", return_value=mock_ts_service),
            patch("app.mcp.mcp.SemanticModelService", return_value=mock_sm_service),
            patch("app.mcp.mcp.TableSchemaResponse"),
            patch("app.mcp.mcp.SemanticModelResponse"),
        ):
            from app.mcp.mcp import get_output_port_model

            result = get_output_port_model(output_port_id=OUTPUT_PORT_ID)

        assert result["output_port"]["tags"] == [
            {"id": str(tag_id), "value": "SENSITIVE"}
        ]
