package provider

import (
	"context"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &DatasetDataSource{}

type DatasetDataSource struct {
	client *sdk.DataProductPortalSDK
}

type DatasetDataSourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	DomainID    types.String `tfsdk:"domain_id"`
}

func NewDatasetDataSource() datasource.DataSource {
	return &DatasetDataSource{}
}

func (d *DatasetDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_dataset"
}

func (d *DatasetDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a dataset from the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id":          schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name":        schema.StringAttribute{Computed: true, Description: "The name."},
			"description": schema.StringAttribute{Computed: true, Description: "The description."},
			"domain_id":   schema.StringAttribute{Computed: true, Description: "The domain ID."},
		},
	}
}

func (d *DatasetDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*sdk.DataProductPortalSDK)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Data Source Configure Type", "Expected *sdk.DataProductPortalSDK")
		return
	}
	d.client = client
}

func (d *DatasetDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data DatasetDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	ds, err := d.client.Datasets.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read dataset: %s", err))
		return
	}

	data.Name = types.StringValue(ds.Name)
	data.Description = types.StringValue(ds.Description)
	data.DomainID = types.StringValue(ds.DomainID)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
