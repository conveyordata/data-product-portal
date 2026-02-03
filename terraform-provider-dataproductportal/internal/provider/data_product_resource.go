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

var _ resource.Resource = &DataProductResource{}

type DataProductResource struct {
	client *portalsdk.Client
}

type DataProductResourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
	About       types.String `tfsdk:"about"`
	DomainID    types.String `tfsdk:"domain_id"`
	TypeID      types.String `tfsdk:"type_id"`
	Namespace   types.String `tfsdk:"namespace"`
	LifecycleID types.String `tfsdk:"lifecycle_id"`
	TagIDs      types.List   `tfsdk:"tag_ids"`
	Owners      types.List   `tfsdk:"owners"`
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
				Required:    true,
				Description: "The namespace of the data product.",
			},
			"lifecycle_id": schema.StringAttribute{
				Required:    true,
				Description: "The ID of the lifecycle.",
			},
			"tag_ids": schema.ListAttribute{
				Required:    true,
				ElementType: types.StringType,
				Description: "List of tag IDs.",
			},
			"owners": schema.ListAttribute{
				Required:    true,
				ElementType: types.StringType,
				Description: "List of owner user IDs.",
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
	client, ok := req.ProviderData.(*portalsdk.Client)
	if !ok {
		resp.Diagnostics.AddError("Unexpected Resource Configure Type", "Expected *portalsdk.Client")
		return
	}
	r.client = client
}

func parseUUIDList(ctx context.Context, list types.List) ([]uuid.UUID, error) {
	var strs []string
	diags := list.ElementsAs(ctx, &strs, false)
	if diags.HasError() {
		return nil, fmt.Errorf("unable to parse list")
	}
	result := make([]uuid.UUID, len(strs))
	for i, s := range strs {
		id, err := uuid.Parse(s)
		if err != nil {
			return nil, fmt.Errorf("invalid UUID %q: %w", s, err)
		}
		result[i] = id
	}
	return result, nil
}

func (r *DataProductResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	domainID, err := uuid.Parse(data.DomainID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain_id: %s", err))
		return
	}
	typeID, err := uuid.Parse(data.TypeID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse type_id: %s", err))
		return
	}
	lifecycleID, err := uuid.Parse(data.LifecycleID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse lifecycle_id: %s", err))
		return
	}
	tagIDs, err := parseUUIDList(ctx, data.TagIDs)
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse tag_ids: %s", err))
		return
	}
	owners, err := parseUUIDList(ctx, data.Owners)
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse owners: %s", err))
		return
	}

	var about *string
	if !data.About.IsNull() {
		v := data.About.ValueString()
		about = &v
	}

	created, err := r.client.CreateDataProduct(ctx, &portalsdk.CreateDataProductRequestOptions{
		Body: &portalsdk.DataProductCreate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
			About:       about,
			DomainID:    domainID,
			TypeID:      typeID,
			Namespace:   data.Namespace.ValueString(),
			LifecycleID: lifecycleID,
			TagIds:      tagIDs,
			Owners:      owners,
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create data product: %s", err))
		return
	}

	dp, err := r.client.GetDataProduct(ctx, &portalsdk.GetDataProductRequestOptions{
		PathParams: &portalsdk.GetDataProductPath{ID: created.ID},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read created data product: %s", err))
		return
	}

	data.ID = types.StringValue(dp.ID.String())
	data.Status = types.StringValue(string(dp.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	dp, err := r.client.GetDataProduct(ctx, &portalsdk.GetDataProductRequestOptions{
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
	data.LifecycleID = types.StringValue(dp.Lifecycle.ID.String())
	data.Status = types.StringValue(string(dp.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}
	domainID, err := uuid.Parse(data.DomainID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain_id: %s", err))
		return
	}
	typeID, err := uuid.Parse(data.TypeID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse type_id: %s", err))
		return
	}
	lifecycleID, err := uuid.Parse(data.LifecycleID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse lifecycle_id: %s", err))
		return
	}
	tagIDs, err := parseUUIDList(ctx, data.TagIDs)
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse tag_ids: %s", err))
		return
	}
	var about *string
	if !data.About.IsNull() {
		v := data.About.ValueString()
		about = &v
	}

	_, err = r.client.UpdateDataProduct(ctx, &portalsdk.UpdateDataProductRequestOptions{
		PathParams: &portalsdk.UpdateDataProductPath{ID: id},
		Body: &portalsdk.DataProductUpdate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
			About:       about,
			DomainID:    domainID,
			TypeID:      typeID,
			Namespace:   data.Namespace.ValueString(),
			LifecycleID: lifecycleID,
			TagIds:      tagIDs,
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update data product: %s", err))
		return
	}

	dp, err := r.client.GetDataProduct(ctx, &portalsdk.GetDataProductRequestOptions{
		PathParams: &portalsdk.GetDataProductPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read updated data product: %s", err))
		return
	}

	data.Status = types.StringValue(string(dp.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DataProductResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data DataProductResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse ID: %s", err))
		return
	}

	_, err = r.client.RemoveDataProduct(ctx, &portalsdk.RemoveDataProductRequestOptions{
		PathParams: &portalsdk.RemoveDataProductPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete data product: %s", err))
	}
}
