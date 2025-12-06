package provider

import (
	"context"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &PlatformDataSource{}

type PlatformDataSource struct {
	client *sdk.DataProductPortalSDK
}

type PlatformDataSourceModel struct {
	ID   types.String `tfsdk:"id"`
	Name types.String `tfsdk:"name"`
}

func NewPlatformDataSource() datasource.DataSource {
	return &PlatformDataSource{}
}

func (d *PlatformDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_platform"
}

func (d *PlatformDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a platform.",
		Attributes: map[string]schema.Attribute{
			"id":   schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name": schema.StringAttribute{Computed: true, Description: "The name."},
		},
	}
}

func (d *PlatformDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	d.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (d *PlatformDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data PlatformDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	item, err := d.client.Platforms.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read: %s", err))
		return
	}
	data.Name = types.StringValue(item.Name)
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
