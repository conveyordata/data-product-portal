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

	requiredAttrs := []string{"name", "description"}
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

func TestOutputPortResource_Metadata(t *testing.T) {
	r := NewOutputPortResource()
	resp := &resource.MetadataResponse{}
	r.Metadata(context.Background(), resource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_output_port" {
		t.Errorf("expected TypeName 'dataproductportal_output_port', got %q", resp.TypeName)
	}
}

func TestOutputPortResource_Schema(t *testing.T) {
	r := NewOutputPortResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	requiredAttrs := []string{"data_product_id", "name", "namespace", "description", "access_type", "tag_ids", "owners"}
	for _, attr := range requiredAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	computedAttrs := []string{"id", "status"}
	for _, attr := range computedAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
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

func TestDataProductResource_Schema(t *testing.T) {
	r := NewDataProductResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	requiredAttrs := []string{"name", "description", "domain_id", "type_id", "namespace", "lifecycle_id", "tag_ids", "owners"}
	for _, attr := range requiredAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	computedAttrs := []string{"id", "status"}
	for _, attr := range computedAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	optionalAttrs := []string{"about"}
	for _, attr := range optionalAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
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

func TestDataProductTypeResource_Schema(t *testing.T) {
	r := NewDataProductTypeResource()
	resp := &resource.SchemaResponse{}
	r.Schema(context.Background(), resource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	requiredAttrs := []string{"name", "description", "icon_key"}
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
}
