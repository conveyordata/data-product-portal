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

var _ resource.Resource = &RoleAssignmentResource{}

type RoleAssignmentResource struct {
	client *sdk.DataProductPortalSDK
}

type RoleAssignmentResourceModel struct {
	ID      types.String `tfsdk:"id"`
	UserID  types.String `tfsdk:"user_id"`
	RoleID  types.String `tfsdk:"role_id"`
	Scope   types.String `tfsdk:"scope"`
	ScopeID types.String `tfsdk:"scope_id"`
}

func NewRoleAssignmentResource() resource.Resource {
	return &RoleAssignmentResource{}
}

func (r *RoleAssignmentResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_role_assignment"
}

func (r *RoleAssignmentResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages a role assignment.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed: true, Description: "The unique identifier.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.UseStateForUnknown()},
			},
			"user_id":  schema.StringAttribute{Required: true, Description: "The user ID."},
			"role_id":  schema.StringAttribute{Required: true, Description: "The role ID."},
			"scope":    schema.StringAttribute{Required: true, Description: "The scope (global, data_product, dataset)."},
			"scope_id": schema.StringAttribute{Optional: true, Description: "The scope resource ID."},
		},
	}
}

func (r *RoleAssignmentResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
	if req.ProviderData == nil {
		return
	}
	r.client = req.ProviderData.(*sdk.DataProductPortalSDK)
}

func (r *RoleAssignmentResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data RoleAssignmentResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	item, err := r.client.RoleAssignments.Create(ctx, &models.RoleAssignmentCreate{
		UserID:  data.UserID.ValueString(),
		RoleID:  data.RoleID.ValueString(),
		Scope:   data.Scope.ValueString(),
		ScopeID: data.ScopeID.ValueString(),
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create: %s", err))
		return
	}
	data.ID = types.StringValue(item.ID)
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *RoleAssignmentResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data RoleAssignmentResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	item, err := r.client.RoleAssignments.Get(ctx, data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read: %s", err))
		return
	}

	data.UserID = types.StringValue(item.UserID)
	data.RoleID = types.StringValue(item.RoleID)
	data.Scope = types.StringValue(item.Scope)
	if item.ScopeID != "" {
		data.ScopeID = types.StringValue(item.ScopeID)
	}
	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *RoleAssignmentResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	// Role assignments are immutable - delete and recreate
	resp.Diagnostics.AddError("Update Not Supported", "Role assignments cannot be updated. Delete and recreate instead.")
}

func (r *RoleAssignmentResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data RoleAssignmentResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}
	if err := r.client.RoleAssignments.Delete(ctx, data.ID.ValueString()); err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete: %s", err))
	}
}
