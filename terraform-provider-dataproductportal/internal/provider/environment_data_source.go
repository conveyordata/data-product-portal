package provider

import (
	"context"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &EnvironmentDataSource{}

type EnvironmentDataSource struct {
	client *sdk.DataProductPortalSDK
}

type EnvironmentDataSourceModel struct {
	ID        types.String `tfsdk:"id"`
	Name      types.String `tfsdk:"name"`
	Acronym   types.String `tfsdk:"acronym"`
	Context   types.String `tfsdk:"context"`
	IsDefault types.Bool   `tfsdk:"is_default"`
}

func NewEnvironmentDataSource() datasource.DataSource {
	return &EnvironmentDataSource{}
}

func (d *EnvironmentDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_environment"
}

func (d *EnvironmentDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches an environment by ID from the list of environments.",
		Attributes: map[string]schema.Attribute{
			"id":         schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name":       schema.StringAttribute{Computed: true, Description: "The name."},
			"acronym":    schema.StringAttribute{Computed: true, Description: "The acronym."},
			"context":    schema.StringAttribute{Computed: true, Description: "The context."},
			"is_default": schema.BoolAttribute{Computed: true, Description: "Whether this is the default environment."},
		},
	}
}

func (d *EnvironmentDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	d.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (d *EnvironmentDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data EnvironmentDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	// API only supports listing, so we find by ID from the list
	items, err := d.client.Environments.List(ctx)
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to list environments: %s", err))
		return
	}

	for _, item := range items {
		if item.ID == data.ID.ValueString() {
			data.Name = types.StringValue(item.Name)
			data.Acronym = types.StringValue(item.Acronym)
			data.Context = types.StringValue(item.Context)
			data.IsDefault = types.BoolValue(item.IsDefault)
			resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
			return
		}
	}

	resp.Diagnostics.AddError("Not Found", fmt.Sprintf("Environment with ID %s not found", data.ID.ValueString()))
}
