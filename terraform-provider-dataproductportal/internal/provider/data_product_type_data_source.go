package provider

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/portalsdk"
	"github.com/google/uuid"
	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ datasource.DataSource = &DataProductTypeDataSource{}

type DataProductTypeDataSource struct {
	client *portalsdk.Client
}

type DataProductTypeDataSourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	IconKey     types.String `tfsdk:"icon_key"`
}

func NewDataProductTypeDataSource() datasource.DataSource {
	return &DataProductTypeDataSource{}
}

func (d *DataProductTypeDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_product_type"
}

func (d *DataProductTypeDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a data product type.",
		Attributes: map[string]schema.Attribute{
			"id":          schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name":        schema.StringAttribute{Computed: true, Description: "The name."},
			"description": schema.StringAttribute{Computed: true, Description: "The description."},
			"icon_key":    schema.StringAttribute{Computed: true, Description: "The icon key."},
		},
	}
}

func (d *DataProductTypeDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*portalsdk.Client)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Data Source Configure Type", "Expected *portalsdk.Client")
		return
	}
	d.client = client
}

func (d *DataProductTypeDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data DataProductTypeDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	item, err := d.client.GetDataProductType(ctx, &portalsdk.GetDataProductTypeRequestOptions{
		PathParams: &portalsdk.GetDataProductTypePath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read: %s", err))
		return
	}
	data.Name = types.StringValue(item.Name)
	data.Description = types.StringValue(item.Description)
	data.IconKey = types.StringValue(string(item.IconKey))
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
