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

var _ datasource.DataSource = &OutputPortDataSource{}

type OutputPortDataSource struct {
	client *portalsdk.Client
}

type OutputPortDataSourceModel struct {
	ID            types.String `tfsdk:"id"`
	DataProductID types.String `tfsdk:"data_product_id"`
	Name          types.String `tfsdk:"name"`
	Namespace     types.String `tfsdk:"namespace"`
	Description   types.String `tfsdk:"description"`
	AccessType    types.String `tfsdk:"access_type"`
	Status        types.String `tfsdk:"status"`
}

func NewOutputPortDataSource() datasource.DataSource {
	return &OutputPortDataSource{}
}

func (d *OutputPortDataSource) Metadata(ctx context.Context, req datasource.MetadataRequest, resp *datasource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_output_port"
}

func (d *OutputPortDataSource) Schema(ctx context.Context, req datasource.SchemaRequest, resp *datasource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Fetches an output port from the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id":              schema.StringAttribute{Required: true, Description: "The unique identifier."},
			"data_product_id": schema.StringAttribute{Required: true, Description: "The data product ID."},
			"name":            schema.StringAttribute{Computed: true, Description: "The name."},
			"namespace":       schema.StringAttribute{Computed: true, Description: "The namespace."},
			"description":     schema.StringAttribute{Computed: true, Description: "The description."},
			"access_type":     schema.StringAttribute{Computed: true, Description: "The access type."},
			"status":          schema.StringAttribute{Computed: true, Description: "The status."},
		},
	}
}

func (d *OutputPortDataSource) Configure(ctx context.Context, req datasource.ConfigureRequest, resp *datasource.ConfigureResponse) {
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

func (d *OutputPortDataSource) Read(ctx context.Context, req datasource.ReadRequest, resp *datasource.ReadResponse) {
	var data OutputPortDataSourceModel
	resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}
	dpID, err := uuid.Parse(data.DataProductID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse data_product_id: %s", err))
		return
	}

	op, err := d.client.GetOutputPort(ctx, &portalsdk.GetOutputPortRequestOptions{
		PathParams: &portalsdk.GetOutputPortPath{DataProductID: dpID, ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read output port: %s", err))
		return
	}

	data.Name = types.StringValue(op.Name)
	data.Namespace = types.StringValue(op.Namespace)
	data.Description = types.StringValue(op.Description)
	data.AccessType = types.StringValue(string(op.AccessType))
	data.Status = types.StringValue(string(op.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
