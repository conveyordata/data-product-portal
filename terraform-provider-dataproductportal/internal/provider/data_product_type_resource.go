package provider

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/portalsdk"
	"github.com/google/uuid"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ resource.Resource = &DataProductTypeResource{}

type DataProductTypeResource struct {
	client *portalsdk.Client
}

type DataProductTypeResourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	IconKey     types.String `tfsdk:"icon_key"`
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
			"name":        schema.StringAttribute{Required: true, Description: "The name."},
			"description": schema.StringAttribute{Required: true, Description: "The description."},
			"icon_key":    schema.StringAttribute{Required: true, Description: "The icon key."},
		},
	}
}

func (r *DataProductTypeResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*portalsdk.Client)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Resource Configure Type", "Expected *portalsdk.Client")
		return
	}
	r.client = client
}

func (r *DataProductTypeResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	created, err := r.client.CreateDataProductType(ctx, &portalsdk.CreateDataProductTypeRequestOptions{
		Body: &portalsdk.DataProductTypeCreate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
			IconKey:     portalsdk.DataProductIconKey(data.IconKey.ValueString()),
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create: %s", err))
		return
	}
	data.ID = types.StringValue(created.ID.String())
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductTypeResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	item, err := r.client.GetDataProductType(ctx, &portalsdk.GetDataProductTypeRequestOptions{
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

func (r *DataProductTypeResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DataProductTypeResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	_, err = r.client.UpdateDataProductType(ctx, &portalsdk.UpdateDataProductTypeRequestOptions{
		PathParams: &portalsdk.UpdateDataProductTypePath{ID: id},
		Body: &portalsdk.DataProductTypeUpdate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
			IconKey:     portalsdk.DataProductIconKey(data.IconKey.ValueString()),
		},
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

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	_, err = r.client.RemoveDataProductType(ctx, &portalsdk.RemoveDataProductTypeRequestOptions{
		PathParams: &portalsdk.RemoveDataProductTypePath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete: %s", err))
	}
}
