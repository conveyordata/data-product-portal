package provider

import (
	"context"
	"encoding/json"
	"fmt"

	sdk "github.com/data-product-portal/sdk-go"
	"github.com/data-product-portal/sdk-go/models"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

var _ resource.Resource = &DataOutputResource{}

type DataOutputResource struct {
	client *sdk.DataProductPortalSDK
}

type DataOutputResourceModel struct {
	ID            types.String `tfsdk:"id"`
	Name          types.String `tfsdk:"name"`
	Description   types.String `tfsdk:"description"`
	OwnerID       types.String `tfsdk:"owner_id"`
	Configuration types.String `tfsdk:"configuration"`
}

func NewDataOutputResource() resource.Resource {
	return &DataOutputResource{}
}

func (r *DataOutputResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_output"
}

func (r *DataOutputResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages a data output.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true, Description: "The unique identifier.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.UseStateForUnknown()},
			},
			"name":          schema.StringAttribute{Required: true, Description: "The name."},
			"description":   schema.StringAttribute{Optional: true, Description: "The description."},
			"owner_id":      schema.StringAttribute{Required: true, Description: "The owner data product ID."},
			"configuration": schema.StringAttribute{Required: true, Description: "JSON configuration."},
		},
	}
}

func (r *DataOutputResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	r.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (r *DataOutputResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DataOutputResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	var config map[string]interface{}
	if err := json.Unmarshal([]byte(data.Configuration.ValueString()), &config); err != nil {
		resp.Diagnostics.AddError("Configuration Error", fmt.Sprintf("Invalid JSON: %s", err))
		return
	}

	item, err := r.client.DataOutputs.Create(ctx, &models.DataOutputCreate{
		Name:          data.Name.ValueString(),
		Description:   data.Description.ValueString(),
		OwnerID:       data.OwnerID.ValueString(),
		Configuration: config,
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create: %s", err))
		return
	}
	data.ID = types.StringValue(item.ID)
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataOutputResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DataOutputResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	item, err := r.client.DataOutputs.Get(ctx, data.ID.ValueString())
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

func (r *DataOutputResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DataOutputResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	var config map[string]interface{}
	if err := json.Unmarshal([]byte(data.Configuration.ValueString()), &config); err != nil {
		resp.Diagnostics.AddError("Configuration Error", fmt.Sprintf("Invalid JSON: %s", err))
		return
	}

	_, err := r.client.DataOutputs.Update(ctx, data.ID.ValueString(), &models.DataOutputCreate{
		Name:          data.Name.ValueString(),
		Description:   data.Description.ValueString(),
		OwnerID:       data.OwnerID.ValueString(),
		Configuration: config,
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update: %s", err))
		return
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataOutputResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data DataOutputResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	if err := r.client.DataOutputs.Delete(ctx, data.ID.ValueString()); err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete: %s", err))
	}
}
