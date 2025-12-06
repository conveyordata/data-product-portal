package provider

import (
	"context"
	"testing"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
)

// Unit tests for data source metadata and schema

func TestDomainDataSource_Metadata(t *testing.T) {
	d := NewDomainDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_domain" {
		t.Errorf("expected TypeName 'dataproductportal_domain', got %q", resp.TypeName)
	}
}

func TestDomainDataSource_Schema(t *testing.T) {
	d := NewDomainDataSource()
	resp := &datasource.SchemaResponse{}
	d.Schema(context.Background(), datasource.SchemaRequest{}, resp)

	if resp.Schema.Attributes == nil {
		t.Fatal("expected schema attributes to be non-nil")
	}

	requiredAttrs := []string{"id"}
	for _, attr := range requiredAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}

	computedAttrs := []string{"name", "description"}
	for _, attr := range computedAttrs {
		if _, ok := resp.Schema.Attributes[attr]; !ok {
			t.Errorf("expected %q attribute in schema", attr)
		}
	}
}

func TestEnvironmentDataSource_Metadata(t *testing.T) {
	d := NewEnvironmentDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_environment" {
		t.Errorf("expected TypeName 'dataproductportal_environment', got %q", resp.TypeName)
	}
}

func TestTagDataSource_Metadata(t *testing.T) {
	d := NewTagDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_tag" {
		t.Errorf("expected TypeName 'dataproductportal_tag', got %q", resp.TypeName)
	}
}

func TestPlatformDataSource_Metadata(t *testing.T) {
	d := NewPlatformDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_platform" {
		t.Errorf("expected TypeName 'dataproductportal_platform', got %q", resp.TypeName)
	}
}

func TestDataOutputDataSource_Metadata(t *testing.T) {
	d := NewDataOutputDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_output" {
		t.Errorf("expected TypeName 'dataproductportal_data_output', got %q", resp.TypeName)
	}
}

func TestDataProductDataSource_Metadata(t *testing.T) {
	d := NewDataProductDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_product" {
		t.Errorf("expected TypeName 'dataproductportal_data_product', got %q", resp.TypeName)
	}
}

func TestDatasetDataSource_Metadata(t *testing.T) {
	d := NewDatasetDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_dataset" {
		t.Errorf("expected TypeName 'dataproductportal_dataset', got %q", resp.TypeName)
	}
}

func TestDataProductTypeDataSource_Metadata(t *testing.T) {
	d := NewDataProductTypeDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_data_product_type" {
		t.Errorf("expected TypeName 'dataproductportal_data_product_type', got %q", resp.TypeName)
	}
}

func TestUserDataSource_Metadata(t *testing.T) {
	d := NewUserDataSource()
	resp := &datasource.MetadataResponse{}
	d.Metadata(context.Background(), datasource.MetadataRequest{ProviderTypeName: "dataproductportal"}, resp)

	if resp.TypeName != "dataproductportal_user" {
		t.Errorf("expected TypeName 'dataproductportal_user', got %q", resp.TypeName)
	}
}
