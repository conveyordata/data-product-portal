package sdk

import (
	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/services"
)

type DataProductPortalSDK struct {
	client                *client.Client
	Domains               *services.DomainService
	DataProducts          *services.DataProductService
	DataProductTypes      *services.DataProductTypeService
	DataProductLifecycles *services.DataProductLifecycleService
	Datasets              *services.DatasetService
	DataOutputs           *services.DataOutputService
	Environments          *services.EnvironmentService
	Platforms             *services.PlatformService
	Tags                  *services.TagService
	Roles                 *services.RoleService
	RoleAssignments       *services.RoleAssignmentService
	Users                 *services.UserService
}

func New(baseURL, apiKey string, opts ...client.ClientOption) *DataProductPortalSDK {
	c := client.NewClient(baseURL, apiKey, opts...)
	return &DataProductPortalSDK{
		client:                c,
		Domains:               services.NewDomainService(c),
		DataProducts:          services.NewDataProductService(c),
		DataProductTypes:      services.NewDataProductTypeService(c),
		DataProductLifecycles: services.NewDataProductLifecycleService(c),
		Datasets:              services.NewDatasetService(c),
		DataOutputs:           services.NewDataOutputService(c),
		Environments:          services.NewEnvironmentService(c),
		Platforms:             services.NewPlatformService(c),
		Tags:                  services.NewTagService(c),
		Roles:                 services.NewRoleService(c),
		RoleAssignments:       services.NewRoleAssignmentService(c),
		Users:                 services.NewUserService(c),
	}
}
