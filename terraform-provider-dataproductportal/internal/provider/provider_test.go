package provider

import (
	"context"
	"os"
	"testing"

	"github.com/hashicorp/terraform-plugin-framework/provider"
	"github.com/hashicorp/terraform-plugin-framework/providerserver"
	"github.com/hashicorp/terraform-plugin-go/tfprotov6"
)

// testAccProtoV6ProviderFactories is used for acceptance testing
var testAccProtoV6ProviderFactories = map[string]func() (tfprotov6.ProviderServer, error){
	"dataproductportal": providerserver.NewProtocol6WithError(New("test")()),
}

func testAccPreCheck(t *testing.T) {
	// Check that required environment variables are set for acceptance tests
	if os.Getenv("DPP_BASE_URL") == "" {
		os.Setenv("DPP_BASE_URL", "http://localhost:5050")
	}
	if os.Getenv("DPP_API_KEY") == "" {
		os.Setenv("DPP_API_KEY", "test-api-key")
	}
}

func TestProvider_Metadata(t *testing.T) {
	p := New("1.0.0")()
	resp := &provider.MetadataResponse{}
	p.Metadata(context.Background(), provider.MetadataRequest{}, resp)

	if resp.TypeName != "dataproductportal" {
		t.Errorf("expected TypeName 'dataproductportal', got %q", resp.TypeName)
	}
	if resp.Version != "1.0.0" {
		t.Errorf("expected Version '1.0.0', got %q", resp.Version)
	}
}

func TestProvider_Schema(t *testing.T) {
	p := New("test")()
	resp := &provider.SchemaResponse{}
	p.Schema(context.Background(), provider.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	if _, ok := resp.Schema.Attributes["base_url"]; !ok {
		t.Error("expected 'base_url' attribute in schema")
	}

	if _, ok := resp.Schema.Attributes["api_key"]; !ok {
		t.Error("expected 'api_key' attribute in schema")
	}
}

func TestProvider_Resources(t *testing.T) {
	p := &DataProductPortalProvider{version: "test"}
	resources := p.Resources(context.Background())

	expectedCount := 9 // domain, data_product, data_product_type, dataset, data_output, environment, platform, tag, role_assignment

	if len(resources) != expectedCount {
		t.Errorf("expected %d resources, got %d", expectedCount, len(resources))
	}
}

func TestProvider_DataSources(t *testing.T) {
	p := &DataProductPortalProvider{version: "test"}
	dataSources := p.DataSources(context.Background())

	expectedCount := 9 // domain, data_product, data_product_type, dataset, data_output, environment, platform, tag, user

	if len(dataSources) != expectedCount {
		t.Errorf("expected %d data sources, got %d", expectedCount, len(dataSources))
	}
}
