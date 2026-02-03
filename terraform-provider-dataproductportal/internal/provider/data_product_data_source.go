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

var _ datasource.DataSource = &DataProductDataSource{}

type DataProductDataSource struct {
	client *portalsdk.Client
}

type DataProductDataSourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	About       types.String `tfsdk:"about"`
	DomainID    types.String `tfsdk:"domain_id"`
	TypeID      types.String `tfsdk:"type_id"`
	Namespace   types.String `tfsdk:"namespace"`
	Status      types.String `tfsdk:"status"`
}

func NewDataProductDataSource() datasource.DataSource {
	return &DataProductDataSource{}
}

func (d *DataProductDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_product"
}

func (d *DataProductDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches a data product from the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id":          schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"name":        schema.StringAttribute{Computed: true, Description: "The name."},
			"description": schema.StringAttribute{Computed: true, Description: "The description."},
			"about":       schema.StringAttribute{Computed: true, Description: "Extended information."},
			"domain_id":   schema.StringAttribute{Computed: true, Description: "The domain ID."},
			"type_id":     schema.StringAttribute{Computed: true, Description: "The type ID."},
			"namespace":   schema.StringAttribute{Computed: true, Description: "The namespace."},
			"status":      schema.StringAttribute{Computed: true, Description: "The status."},
		},
	}
}

func (d *DataProductDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
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

func (d *DataProductDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data DataProductDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	dp, err := d.client.GetDataProduct(ctx, &portalsdk.GetDataProductRequestOptions{
		PathParams: &portalsdk.GetDataProductPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read data product: %s", err))
		return
	}

	data.Name = types.StringValue(dp.Name)
	data.Description = types.StringValue(dp.Description)
	data.About = types.StringValue(dp.About)
	data.DomainID = types.StringValue(dp.Domain.ID.String())
	data.TypeID = types.StringValue(dp.Type.ID.String())
	data.Namespace = types.StringValue(dp.Namespace)
	data.Status = types.StringValue(string(dp.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
