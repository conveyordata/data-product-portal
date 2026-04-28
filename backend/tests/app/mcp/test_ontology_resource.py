from app.mcp.mcp import get_ontology_resource  # type: ignore[attr-defined]


class TestOntologyResource:
    @classmethod
    def setup_class(cls):
        cls.content = get_ontology_resource()

    def test_returns_a_string(self):
        assert isinstance(self.content, str)

    def test_is_not_empty(self):
        assert len(self.content) > 200

    def test_contains_entity_model_section(self):
        assert "## Entity Model" in self.content

    def test_contains_all_five_entities(self):
        assert "### Domain" in self.content
        assert "### Data Product" in self.content
        assert "### Output Port" in self.content
        assert "### Technical Asset" in self.content
        assert "### Input Port" in self.content

    def test_contains_relationships_section(self):
        assert "## Relationships" in self.content
        assert "-[contains]->" in self.content
        assert "-[exposes]->" in self.content
        assert "-[consumes via Input Port]->" in self.content

    def test_contains_access_flow_section(self):
        assert "## Access Flow" in self.content
        assert "PENDING" in self.content
        assert "APPROVED" in self.content
        assert "DENIED" in self.content

    def test_contains_id_provenance_for_each_entity(self):
        assert "get_marketplace_overview()" in self.content
        assert "search_data_products()" in self.content
        assert "search_output_ports()" in self.content
        assert "get_data_product_analytics()" in self.content

    def test_contains_resolved_by_for_each_entity(self):
        assert "get_domain_details" in self.content
        assert "get_data_product_details" in self.content
        assert "get_output_port_details" in self.content
        assert "get_output_port_model" in self.content
        assert "get_technical_asset_details" in self.content
