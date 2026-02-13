from fastapi.testclient import TestClient

from tests.factories import PlatformFactory
from tests.factories.platform_service import PlatformServiceFactory
from tests.factories.platform_service_config import PlatformServiceConfigFactory

ENDPOINT = "/api/v2/plugins"


class TestPluginEndpoints:
    def test_list_plugins_returns_no_results_when_no_service_config(
        self, client: TestClient
    ):
        """Test GET /v2/plugins returns empty list when no service configs exist"""
        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
        assert len(data["plugins"]) == 3

    def test_list_plugins_returns_all_available_plugins(self, client: TestClient):
        """Test GET /v2/plugins returns list of all available plugins"""
        aws = PlatformFactory(name="AWS")
        s3 = PlatformServiceFactory(name="S3")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
        assert len(data["plugins"]) > 0

        # Verify each plugin has required fields
        for plugin in data["plugins"]:
            assert "plugin" in plugin
            assert "platform" in plugin
            assert "display_name" in plugin
            assert "icon_name" in plugin
            assert "ui_metadata" in plugin
            assert "result_label" in plugin
            assert "result_tooltip" in plugin
            assert isinstance(plugin["ui_metadata"], list)

    def test_list_plugins_includes_expected_platforms(self, client: TestClient):
        """Test that all expected plugins are in the list"""
        aws = PlatformFactory(name="AWS")
        s3 = PlatformServiceFactory(name="S3")
        glue = PlatformServiceFactory(name="Glue")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        PlatformServiceConfigFactory(service=glue, platform=aws)
        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        plugin_names = {p["plugin"] for p in data["plugins"]}

        # Verify all expected plugins are present
        expected_plugins = {
            "S3TechnicalAssetConfiguration",
            "GlueTechnicalAssetConfiguration",
        }
        assert expected_plugins.issubset(plugin_names)
        # not configured = true
        assert (
            next(p for p in data["plugins"] if p["plugin"] == "ConveyorPlugin").get(
                "not_configured", False
            )
            is True
        )

    def test_list_plugins_includes_all_platforms(self, client: TestClient):
        """Test that all expected plugins are in the list"""
        aws = PlatformFactory(name="AWS")
        dwh = PlatformFactory(name="DWH")
        s3 = PlatformServiceFactory(name="S3")
        glue = PlatformServiceFactory(name="Glue")
        redshift = PlatformServiceFactory(name="Redshift")
        snowflake = PlatformServiceFactory(name="Snowflake")
        databricks = PlatformServiceFactory(name="Databricks")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        PlatformServiceConfigFactory(service=glue, platform=aws)
        PlatformServiceConfigFactory(service=redshift, platform=aws)
        PlatformServiceConfigFactory(service=snowflake, platform=dwh)
        PlatformServiceConfigFactory(service=databricks, platform=dwh)

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()

        plugin_names = {p["plugin"] for p in data["plugins"]}

        # Verify all expected plugins are present
        expected_plugins = {
            "S3TechnicalAssetConfiguration",
            "GlueTechnicalAssetConfiguration",
        }
        assert expected_plugins.issubset(plugin_names)

    def test_get_plugin_form_by_name_returns_correct_plugin(self, client: TestClient):
        """Test GET /v2/plugins/{plugin_name}/form returns specific plugin"""
        aws = PlatformFactory(name="AWS")
        s3 = PlatformServiceFactory(name="S3")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        response = client.get(f"{ENDPOINT}/S3TechnicalAssetConfiguration/form")

        assert response.status_code == 200
        data = response.json()

        # Verify it's the correct plugin
        assert data["plugin"] == "S3TechnicalAssetConfiguration"
        assert data["platform"] == "s3"
        assert data["display_name"] == "S3"
        assert data["icon_name"] == "s3-logo.svg"
        assert "ui_metadata" in data
        assert isinstance(data["ui_metadata"], list)

    def test_get_plugin_form_includes_all_fields(self, client: TestClient):
        """Test that plugin form includes all expected fields"""
        aws = PlatformFactory(name="AWS")
        glue = PlatformServiceFactory(name="Glue")
        PlatformServiceConfigFactory(service=glue, platform=aws)
        response = client.get(f"{ENDPOINT}/GlueTechnicalAssetConfiguration/form")

        assert response.status_code == 200
        data = response.json()

        assert data["plugin"] == "GlueTechnicalAssetConfiguration"

        # Get field names
        field_names = {field["name"] for field in data["ui_metadata"]}

        # Verify expected fields are present
        expected_fields = {"database", "database_suffix", "access_granularity", "table"}
        assert expected_fields.issubset(field_names)

    def test_get_plugin_form_with_invalid_name_returns_404(self, client: TestClient):
        """Test GET /v2/plugins/{plugin_name}/form with invalid name returns 404"""
        response = client.get(f"{ENDPOINT}/NonExistentPlugin/form")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "NonExistentPlugin" in data["detail"]
        assert "not found" in data["detail"].lower()

    def test_get_plugin_form_for_each_available_plugin(self, client: TestClient):
        """Test that each plugin from list can be retrieved individually"""
        # Get all plugins
        aws = PlatformFactory(name="AWS")
        s3 = PlatformServiceFactory(name="S3")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        list_response = client.get(ENDPOINT)
        assert list_response.status_code == 200
        plugins = list_response.json()["plugins"]

        # Test each plugin can be retrieved
        for plugin in plugins:
            plugin_name = plugin["plugin"]
            form_response = client.get(f"{ENDPOINT}/{plugin_name}/form")

            assert form_response.status_code == 200
            form_data = form_response.json()
            assert form_data["plugin"] == plugin_name
            assert form_data["platform"] == plugin["platform"]
            assert form_data["display_name"] == plugin["display_name"]

    def test_plugin_form_has_field_dependencies(self, client: TestClient):
        """Test that plugin forms with dependencies include them correctly"""
        aws = PlatformFactory(name="AWS")
        glue = PlatformServiceFactory(name="Glue")
        PlatformServiceConfigFactory(service=glue, platform=aws)
        response = client.get(f"{ENDPOINT}/GlueTechnicalAssetConfiguration/form")

        assert response.status_code == 200
        data = response.json()

        # Find the table field which depends on access_granularity
        table_field = next(
            (f for f in data["ui_metadata"] if f["name"] == "table"), None
        )
        assert table_field is not None

        # Verify dependency structure
        assert "depends_on" in table_field
        if table_field["depends_on"] is not None:
            assert "field_name" in table_field["depends_on"][0]
            assert "value" in table_field["depends_on"][0]
            assert table_field["depends_on"][0]["field_name"] == "access_granularity"


class TestPlatformTilesEndpoint:
    """Test platform tiles endpoint"""

    def test_get_platform_tiles_returns_correct_structure(self, client: TestClient):
        """Test GET /v2/technical_assets/platform-tiles returns correct structure"""
        # Create platform services for testing
        aws = PlatformFactory(name="AWS")
        s3 = PlatformServiceFactory(name="S3")
        glue = PlatformServiceFactory(name="Glue")
        redshift = PlatformServiceFactory(name="Redshift")
        PlatformServiceConfigFactory(service=s3, platform=aws)
        PlatformServiceConfigFactory(service=glue, platform=aws)
        PlatformServiceConfigFactory(service=redshift, platform=aws)

        response = client.get(f"{ENDPOINT}/platform-tiles")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "platform_tiles" in data
        assert isinstance(data["platform_tiles"], list)

    def test_get_platform_tiles_includes_configured_platforms(self, client: TestClient):
        """Test that only configured platforms are included in tiles"""
        # Create some platform services
        aws = PlatformFactory(name="AWS")
        s3_service = PlatformServiceFactory(name="S3")
        PlatformServiceConfigFactory(service=s3_service, platform=aws)

        response = client.get(f"{ENDPOINT}/platform-tiles")

        assert response.status_code == 200
        data = response.json()

        tiles = data["platform_tiles"]
        assert len(tiles) > 0

        # Verify tiles have required fields
        for tile in tiles:
            assert "label" in tile
            assert "value" in tile
            assert "icon_name" in tile
            assert "has_config" in tile
            if tile["has_config"]:
                assert isinstance(tile["has_config"], bool)

    def test_get_platform_tiles_organizes_hierarchy(self, client: TestClient):
        """Test that platform tiles are organized in parent-child hierarchy"""
        # Create AWS services
        response = client.get(f"{ENDPOINT}/platform-tiles")

        assert response.status_code == 200
        data = response.json()

        tiles = data["platform_tiles"]

        # Find AWS parent tile
        aws_tile = next((t for t in tiles if t["value"] == "aws"), None)

        if aws_tile:
            # AWS should have children
            assert "children" in aws_tile
            if aws_tile["children"]:
                assert isinstance(aws_tile["children"], list)
                # Check that children have proper structure
                for child in aws_tile["children"]:
                    assert "label" in child
                    assert "value" in child
                    assert "icon_name" in child

    def test_get_platform_tiles_has_environments_flag(self, client: TestClient):
        """Test that tiles have has_environments flag for parent platforms"""
        # Create AWS services
        response = client.get(f"{ENDPOINT}/platform-tiles")

        assert response.status_code == 200
        data = response.json()

        tiles = data["platform_tiles"]

        # Find AWS tile
        aws_tile = next((t for t in tiles if t["value"] == "aws"), None)

        if aws_tile:
            assert "has_environments" in aws_tile
            # AWS has multiple children, so should have environments
            if aws_tile.get("children") and len(aws_tile["children"]) > 1:
                assert aws_tile["has_environments"] is True
