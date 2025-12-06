package provider

import (
	"context"
	"os"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/provider"
	"github.com/hashicorp/terraform-plugin-framework/provider/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ provider.Provider = &DataProductPortalProvider{}

type DataProductPortalProvider struct {
	version string
}

type DataProductPortalProviderModel struct {
	BaseURL types.String `tfsdk:"base_url"`
	APIKey  types.String `tfsdk:"api_key"`
}

func New(version string) func() provider.Provider {
	return func() provider.Provider {
		return &DataProductPortalProvider{
			version: version,
		}
	}
}

func (p *DataProductPortalProvider) Metadata(ctx context.Context, req provider.MetadataRequest, resp *provider.MetadataResponse) {
	resp.TypeName = "dataproductportal"
	resp.Version = p.version
}

func (p *DataProductPortalProvider) Schema(ctx context.Context, req provider.SchemaRequest, resp *provider.SchemaResponse) {
	resp.Schema = schema.Schema{
		Attributes: map[string]schema.Attribute{
			"base_url": schema.StringAttribute{
				Optional:    true,
				Description: "The base URL of the Data Product Portal API. Can also be set via DPP_BASE_URL environment variable.",
			},
			"api_key": schema.StringAttribute{
				Optional:    true,
				Sensitive:   true,
				Description: "The API key for authentication. Can also be set via DPP_API_KEY environment variable.",
			},
		},
	}
}

func (p *DataProductPortalProvider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) {
	var config DataProductPortalProviderModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &config)...)
	if resp.Diagnostics.HasError() {
		return
	}

	baseURL := os.Getenv("DPP_BASE_URL")
	if !config.BaseURL.IsNull() {
		baseURL = config.BaseURL.ValueString()
	}

	apiKey := os.Getenv("DPP_API_KEY")
	if !config.APIKey.IsNull() {
		apiKey = config.APIKey.ValueString()
	}

	if baseURL == "" {
		resp.Diagnostics.AddError(
			"Missing Base URL",
			"The provider cannot create the Data Product Portal client as there is a missing or empty value for the base URL. "+
				"Set the base_url value in the configuration or use the DPP_BASE_URL environment variable.",
		)
		return
	}

	if apiKey == "" {
		resp.Diagnostics.AddError(
			"Missing API Key",
			"The provider cannot create the Data Product Portal client as there is a missing or empty value for the API key. "+
				"Set the api_key value in the configuration or use the DPP_API_KEY environment variable.",
		)
		return
	}

	client := sdk.New(baseURL, apiKey)
	resp.DataSourceData = client
	resp.ResourceData = client
}

func (p *DataProductPortalProvider) Resources(ctx context.Context) []func() resource.Resource {
	return []func() resource.Resource{
		NewDomainResource,
		NewDataProductResource,
		NewDataProductTypeResource,
		NewDatasetResource,
		NewDataOutputResource,
		NewEnvironmentResource,
		NewPlatformResource,
		NewTagResource,
		NewRoleAssignmentResource,
	}
}

func (p *DataProductPortalProvider) DataSources(ctx context.Context) []func() datasource.DataSource {
	return []func() datasource.DataSource{
		NewDomainDataSource,
		NewDataProductDataSource,
		NewDataProductTypeDataSource,
		NewDatasetDataSource,
		NewDataOutputDataSource,
		NewEnvironmentDataSource,
		NewPlatformDataSource,
		NewTagDataSource,
		NewUserDataSource,
	}
}
