package provider

import (
	"context"
	"testing"

	"github.com/hashicorp/terraform-plugin-framework/resource"
)

// Unit tests for resource metadata and schema

func TestDomainResource_Metadata(t *testing.T) {
	r := NewDomainResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_domain" {
		t.Errorf("expected TypeName 'dataproductportal_domain', got %q", resp.TypeName)
	}
}

func TestDomainResource_Schema(t *testing.T) {
	r := NewDomainResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	requiredAttrs := []string{"name"}
	for _, attr := range requiredAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	computedAttrs := []string{"id"}
	for _, attr := range computedAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	optionalAttrs := []string{"description"}
	for _, attr := range optionalAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}
}

func TestEnvironmentResource_Metadata(t *testing.T) {
	r := NewEnvironmentResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_environment" {
		t.Errorf("expected TypeName 'dataproductportal_environment', got %q", resp.TypeName)
	}
}

func TestEnvironmentResource_Schema(t *testing.T) {
	r := NewEnvironmentResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	if _, ok := resp.Schema.Attributes["id"]; !ok {
		t.Error("expected 'id' attribute in schema")
	}
	if _, ok := resp.Schema.Attributes["name"]; !ok {
		t.Error("expected 'name' attribute in schema")
	}
}

func TestTagResource_Metadata(t *testing.T) {
	r := NewTagResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_tag" {
		t.Errorf("expected TypeName 'dataproductportal_tag', got %q", resp.TypeName)
	}
}

func TestTagResource_Schema(t *testing.T) {
	r := NewTagResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	if _, ok := resp.Schema.Attributes["id"]; !ok {
		t.Error("expected 'id' attribute in schema")
	}
	if _, ok := resp.Schema.Attributes["value"]; !ok {
		t.Error("expected 'value' attribute in schema")
	}
}

func TestPlatformResource_Metadata(t *testing.T) {
	r := NewPlatformResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_platform" {
		t.Errorf("expected TypeName 'dataproductportal_platform', got %q", resp.TypeName)
	}
}

func TestDataOutputResource_Metadata(t *testing.T) {
	r := NewDataOutputResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_output" {
		t.Errorf("expected TypeName 'dataproductportal_data_output', got %q", resp.TypeName)
	}
}

func TestDataProductResource_Metadata(t *testing.T) {
	r := NewDataProductResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_product" {
		t.Errorf("expected TypeName 'dataproductportal_data_product', got %q", resp.TypeName)
	}
}

func TestDatasetResource_Metadata(t *testing.T) {
	r := NewDatasetResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_dataset" {
		t.Errorf("expected TypeName 'dataproductportal_dataset', got %q", resp.TypeName)
	}
}

func TestDataProductTypeResource_Metadata(t *testing.T) {
	r := NewDataProductTypeResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_product_type" {
		t.Errorf("expected TypeName 'dataproductportal_data_product_type', got %q", resp.TypeName)
	}
}

func TestRoleAssignmentResource_Metadata(t *testing.T) {
	r := NewRoleAssignmentResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_role_assignment" {
		t.Errorf("expected TypeName 'dataproductportal_role_assignment', got %q", resp.TypeName)
	}
}
