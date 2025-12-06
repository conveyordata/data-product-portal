package provider

import (
	"context"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/data-product-portal/sdk-go/models"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ resource.Resource = &DataProductTypeResource{}

type DataProductTypeResource struct {
	client *sdk.DataProductPortalSDK
}

type DataProductTypeResourceModel struct {
	ID      types.String `tfsdk:"id"`
	Name    types.String `tfsdk:"name"`
	IconKey types.String `tfsdk:"icon_key"`
}

func NewDataProductTypeResource() resource.Resource {
	return &DataProductTypeResource{}
}

func (r *DataProductTypeResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_product_type"
}

func (r *DataProductTypeResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages a data product type.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true, Description: "The unique identifier.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.UseStateForUnknown()},
			},
			"name":     schema.StringAttribute{Required: true, Description: "The name."},
			"icon_key": schema.StringAttribute{Required: true, Description: "The icon key."},
		},
	}
}

func (r *DataProductTypeResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	r.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (r *DataProductTypeResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	item, err := r.client.DataProductTypes.Create(ctx, &models.DataProductTypeCreate{
		Name:    data.Name.ValueString(),
		IconKey: data.IconKey.ValueString(),
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create: %s", err))
		return
	}
	data.ID = types.StringValue(item.ID)
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductTypeResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	item, err := r.client.DataProductTypes.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read: %s", err))
		return
	}
	data.Name = types.StringValue(item.Name)
	data.IconKey = types.StringValue(item.IconKey)
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductTypeResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	_, err := r.client.DataProductTypes.Update(ctx, data.ID.ValueString(), &models.DataProductTypeCreate{
		Name:    data.Name.ValueString(),
		IconKey: data.IconKey.ValueString(),
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update: %s", err))
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductTypeResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	if err := r.client.DataProductTypes.Delete(ctx, data.ID.ValueString()); err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete: %s", err))
	}
}
