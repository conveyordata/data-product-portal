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

var _ resource.Resource = &OutputPortResource{}

type OutputPortResource struct {
	client *portalsdk.Client
}

type OutputPortResourceModel struct {
	ID            types.String `tfsdk:"id"`
	DataProductID types.String `tfsdk:"data_product_id"`
	Name          types.String `tfsdk:"name"`
	Namespace     types.String `tfsdk:"namespace"`
	Description   types.String `tfsdk:"description"`
	AccessType    types.String `tfsdk:"access_type"`
	TagIDs        types.List   `tfsdk:"tag_ids"`
	Owners        types.List   `tfsdk:"owners"`
	Status        types.String `tfsdk:"status"`
}

func NewOutputPortResource() resource.Resource {
	return &OutputPortResource{}
}

func (r *OutputPortResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_output_port"
}

func (r *OutputPortResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages an output port in the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true, Description: "The unique identifier.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.UseStateForUnknown()},
			},
			"data_product_id": schema.StringAttribute{
				Required:    true,
				Description: "The ID of the data product this output port belongs to.",
			},
			"name": schema.StringAttribute{
				Required:    true,
				Description: "The name.",
			},
			"namespace": schema.StringAttribute{
				Required:    true,
				Description: "The namespace.",
			},
			"description": schema.StringAttribute{
				Required:    true,
				Description: "The description.",
			},
			"access_type": schema.StringAttribute{
				Required:    true,
				Description: "The access type (private, internal, public).",
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
				Description: "The status.",
			},
		},
	}
}

func (r *OutputPortResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
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

func (r *OutputPortResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data OutputPortResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	dpID, err := uuid.Parse(data.DataProductID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse data_product_id: %s", err))
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

	created, err := r.client.CreateOutputPort(ctx, &portalsdk.CreateOutputPortRequestOptions{
		PathParams: &portalsdk.CreateOutputPortPath{DataProductID: dpID},
		Body: &portalsdk.CreateOutputPortRequest{
			Name:        data.Name.ValueString(),
			Namespace:   data.Namespace.ValueString(),
			Description: data.Description.ValueString(),
			AccessType:  portalsdk.OutputPortAccessType(data.AccessType.ValueString()),
			TagIds:      tagIDs,
			Owners:      owners,
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create output port: %s", err))
		return
	}

	op, err := r.client.GetOutputPort(ctx, &portalsdk.GetOutputPortRequestOptions{
		PathParams: &portalsdk.GetOutputPortPath{DataProductID: dpID, ID: created.ID},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read created output port: %s", err))
		return
	}

	data.ID = types.StringValue(op.ID.String())
	data.Status = types.StringValue(string(op.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *OutputPortResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data OutputPortResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
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

	op, err := r.client.GetOutputPort(ctx, &portalsdk.GetOutputPortRequestOptions{
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

func (r *OutputPortResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data OutputPortResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
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
	tagIDs, err := parseUUIDList(ctx, data.TagIDs)
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse tag_ids: %s", err))
		return
	}

	_, err = r.client.UpdateOutputPort(ctx, &portalsdk.UpdateOutputPortRequestOptions{
		PathParams: &portalsdk.UpdateOutputPortPath{DataProductID: dpID, ID: id},
		Body: &portalsdk.DatasetUpdate{
			Name:        data.Name.ValueString(),
			Namespace:   data.Namespace.ValueString(),
			Description: data.Description.ValueString(),
			AccessType:  portalsdk.OutputPortAccessType(data.AccessType.ValueString()),
			TagIds:      tagIDs,
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update output port: %s", err))
		return
	}

	op, err := r.client.GetOutputPort(ctx, &portalsdk.GetOutputPortRequestOptions{
		PathParams: &portalsdk.GetOutputPortPath{DataProductID: dpID, ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read updated output port: %s", err))
		return
	}

	data.Status = types.StringValue(string(op.Status))

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *OutputPortResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data OutputPortResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
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

	_, err = r.client.RemoveDataset(ctx, &portalsdk.RemoveDatasetRequestOptions{
		PathParams: &portalsdk.RemoveDatasetPath{DataProductID: dpID, ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete output port: %s", err))
	}
}
