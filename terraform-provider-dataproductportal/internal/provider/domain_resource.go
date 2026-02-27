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

var _ resource.Resource = &DomainResource{}
var _ resource.ResourceWithImportState = &DomainResource{}

type DomainResource struct {
	client *portalsdk.Client
}

type DomainResourceModel struct {
	ID          types.String `tfsdk:"id"`
	Name        types.String `tfsdk:"name"`
	Description types.String `tfsdk:"description"`
}

func NewDomainResource() resource.Resource {
	return &DomainResource{}
}

func (r *DomainResource) Metadata(ctx context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
	resp.TypeName = req.ProviderTypeName + "_domain"
}

func (r *DomainResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
	resp.Schema = schema.Schema{
		Description: "Manages a domain in the Data Product Portal.",
		Attributes: map[string]schema.Attribute{
			"id": schema.StringAttribute{
				Computed:    true,
				Description: "The unique identifier of the domain.",
				PlanModifiers: []planmodifier.String{
					stringplanmodifier.UseStateForUnknown(),
				},
			},
			"name": schema.StringAttribute{
				Required:    true,
				Description: "The name of the domain.",
			},
			"description": schema.StringAttribute{
				Required:    true,
				Description: "The description of the domain.",
			},
		},
	}
}

func (r *DomainResource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
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

func (r *DomainResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
	var data DomainResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	created, err := r.client.CreateDomain(ctx, &portalsdk.CreateDomainRequestOptions{
		Body: &portalsdk.DomainCreate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to create domain: %s", err))
		return
	}

	domain, err := r.client.GetDomain(ctx, &portalsdk.GetDomainRequestOptions{
		PathParams: &portalsdk.GetDomainPath{ID: created.ID},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read created domain: %s", err))
		return
	}

	data.ID = types.StringValue(domain.ID.String())
	data.Name = types.StringValue(domain.Name)
	data.Description = types.StringValue(domain.Description)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DomainResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
	var data DomainResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain ID: %s", err))
		return
	}

	domain, err := r.client.GetDomain(ctx, &portalsdk.GetDomainRequestOptions{
		PathParams: &portalsdk.GetDomainPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read domain: %s", err))
		return
	}

	data.Name = types.StringValue(domain.Name)
	data.Description = types.StringValue(domain.Description)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DomainResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
	var data DomainResourceModel
	resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain ID: %s", err))
		return
	}

	_, err = r.client.UpdateDomain(ctx, &portalsdk.UpdateDomainRequestOptions{
		PathParams: &portalsdk.UpdateDomainPath{ID: id},
		Body: &portalsdk.DomainUpdate{
			Name:        data.Name.ValueString(),
			Description: data.Description.ValueString(),
		},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to update domain: %s", err))
		return
	}

	domain, err := r.client.GetDomain(ctx, &portalsdk.GetDomainRequestOptions{
		PathParams: &portalsdk.GetDomainPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to read updated domain: %s", err))
		return
	}

	data.Name = types.StringValue(domain.Name)
	data.Description = types.StringValue(domain.Description)

	resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}

func (r *DomainResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
	var data DomainResourceModel
	resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
	if resp.Diagnostics.HasError() {
		return
	}

	id, err := uuid.Parse(data.ID.ValueString())
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain ID: %s", err))
		return
	}

	_, err = r.client.RemoveDomain(ctx, &portalsdk.RemoveDomainRequestOptions{
		PathParams: &portalsdk.RemoveDomainPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to delete domain: %s", err))
		return
	}
}

func (r *DomainResource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
	id, err := uuid.Parse(req.ID)
	if err != nil {
		resp.Diagnostics.AddError("Invalid ID", fmt.Sprintf("Unable to parse domain ID: %s", err))
		return
	}

	domain, err := r.client.GetDomain(ctx, &portalsdk.GetDomainRequestOptions{
		PathParams: &portalsdk.GetDomainPath{ID: id},
	})
	if err != nil {
		resp.Diagnostics.AddError("Client Error", fmt.Sprintf("Unable to import domain: %s", err))
		return
	}

	resp.Diagnostics.Append(resp.State.Set(ctx, &DomainResourceModel{
		ID:          types.StringValue(domain.ID.String()),
		Name:        types.StringValue(domain.Name),
		Description: types.StringValue(domain.Description),
	})...)
}
