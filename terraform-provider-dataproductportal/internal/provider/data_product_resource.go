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

var _ resource.Resource = &DataProductResource{}

type DataProductResource struct {
	client *sdk.DataProductPortalSDK
}

type DataProductResourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	About       types.String `tfsdk:"about"`
	DomainID    types.String `tfsdk:"domain_id"`
	TypeID      types.String `tfsdk:"type_id"`
	Namespace   types.String `tfsdk:"namespace"`
	Status      types.String `tfsdk:"status"`
}

func NewDataProductResource() resource.Resource {
	return &DataProductResource{}
}

func (r *DataProductResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_data_product"
}

func (r *DataProductResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages a data product in the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed:      true,
				Description:   "The unique identifier of the data product.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.UseStateForUnknown()},
			},
			"name": schema.StringAttribute{
				Required:    true,
				Description: "The name of the data product.",
			},
			"description": schema.StringAttribute{
				Required:    true,
				Description: "The description of the data product.",
			},
			"about": schema.StringAttribute{
				Optional:    true,
				Description: "Extended information about the data product.",
			},
			"domain_id": schema.StringAttribute{
				Required:    true,
				Description: "The ID of the domain this data product belongs to.",
			},
			"type_id": schema.StringAttribute{
				Required:    true,
				Description: "The ID of the data product type.",
			},
			"namespace": schema.StringAttribute{
				Computed:    true,
				Description: "The namespace of the data product.",
			},
			"status": schema.StringAttribute{
				Computed:    true,
				Description: "The status of the data product.",
			},
		},
	}
}

func (r *DataProductResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	client, ok := req.ProviderData.(*sdk.DataProductPortalSDK)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Resource Configure Type", "Expected *sdk.DataProductPortalSDK")
		return
	}
	r.client = client
}

func (r *DataProductResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	var about *string
	if !data.About.IsNull() {
		v := data.About.ValueString()
		about = &v
	}

	dp, err := r.client.DataProducts.Create(ctx, &models.DataProductCreate{
		Name:        data.Name.ValueString(),
		Description: data.Description.ValueString(),
		About:       about,
		DomainID:    data.DomainID.ValueString(),
		TypeID:      data.TypeID.ValueString(),
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create data product: %s", err))
		return
	}

	data.ID = types.StringValue(dp.ID)
	data.Namespace = types.StringValue(dp.Namespace)
	data.Status = types.StringValue(dp.Status)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	dp, err := r.client.DataProducts.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read data product: %s", err))
		return
	}

	data.Name = types.StringValue(dp.Name)
	data.Description = types.StringValue(dp.Description)
	if dp.About != nil {
		data.About = types.StringValue(*dp.About)
	}
	data.DomainID = types.StringValue(dp.DomainID)
	data.TypeID = types.StringValue(dp.TypeID)
	data.Namespace = types.StringValue(dp.Namespace)
	data.Status = types.StringValue(dp.Status)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	var about *string
	if !data.About.IsNull() {
		v := data.About.ValueString()
		about = &v
	}

	dp, err := r.client.DataProducts.Update(ctx, data.ID.ValueString(), &models.DataProductCreate{
		Name:        data.Name.ValueString(),
		Description: data.Description.ValueString(),
		About:       about,
		DomainID:    data.DomainID.ValueString(),
		TypeID:      data.TypeID.ValueString(),
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update data product: %s", err))
		return
	}

	data.Namespace = types.StringValue(dp.Namespace)
	data.Status = types.StringValue(dp.Status)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	err := r.client.DataProducts.Delete(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete data product: %s", err))
	}
}
