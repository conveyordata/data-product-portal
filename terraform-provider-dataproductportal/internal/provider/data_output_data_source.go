package provider

import (
	"context"
	"encoding/json"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &DataOutputDataSource{}

type DataOutputDataSource struct {
	client *sdk.DataProductPortalSDK
}

type DataOutputDataSourceModel struct {
	ID            types.String `tfsdk:"id"`
	Name          types.String `tfsdk:"name"`
	Description   types.String `tfsdk:"description"`
	OwnerID       types.String `tfsdk:"owner_id"`
	Configuration types.String `tfsdk:"configuration"`
}

func NewDataOutputDataSource() datasource.DataSource {
	return &DataOutputDataSource{}
}

func (d *DataOutputDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_output"
}

func (d *DataOutputDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a data output.",
		Attributes: map[string]schema.Attribute{
			"id":            schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name":          schema.StringAttribute{Computed: true, Description: "The name."},
			"description":   schema.StringAttribute{Computed: true, Description: "The description."},
			"owner_id":      schema.StringAttribute{Computed: true, Description: "The owner data product ID."},
			"configuration": schema.StringAttribute{Computed: true, Description: "JSON configuration."},
		},
	}
}

func (d *DataOutputDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	d.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (d *DataOutputDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data DataOutputDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	item, err := d.client.DataOutputs.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read: %s", err))
		return
	}

	configBytes, _ := json.Marshal(item.Configuration)
	data.Name = types.StringValue(item.Name)
	data.Description = types.StringValue(item.Description)
	data.OwnerID = types.StringValue(item.OwnerID)
	data.Configuration = types.StringValue(string(configBytes))
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
