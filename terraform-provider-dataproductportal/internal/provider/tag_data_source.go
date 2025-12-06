package provider

import (
	"context"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &TagDataSource{}

type TagDataSource struct {
	client *sdk.DataProductPortalSDK
}

type TagDataSourceModel struct {
	ID    types.String `tfsdk:"id"`
	Value types.String `tfsdk:"value"`
}

func NewTagDataSource() datasource.DataSource {
	return &TagDataSource{}
}

func (d *TagDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_tag"
}

func (d *TagDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a tag.",
		Attributes: map[string]schema.Attribute{
			"id":    schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"value": schema.StringAttribute{Computed: true, Description: "The tag value."},
		},
	}
}

func (d *TagDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	d.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (d *TagDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data TagDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	// List all tags and find by ID (API doesn't support Get by ID)
	items, err := d.client.Tags.List(ctx)
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to list tags: %s", err))
		return
	}
	var found bool
	for _, item := range items {
		if item.ID == data.ID.ValueString() {
			data.Value = types.StringValue(item.Value)
			found = true
			break
		}
	}
	if !found {
		resp.Diagnostics.AddError("Not Found", fmt.Sprintf("Tag with ID %s not found", data.ID.ValueString()))
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
