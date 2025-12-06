package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type RoleService struct {
	client *client.Client
}

func NewRoleService(c *client.Client) *RoleService {
	return &RoleService{client: c}
}

func (s *RoleService) List(ctx context.Context) ([]models.Role, error) {
	var items []models.Role
	err := s.client.Get(ctx, "/api/roles", &items)
	return items, err
}

func (s *RoleService) Get(ctx context.Context, id string) (*models.Role, error) {
	var item models.Role
	err := s.client.Get(ctx, fmt.Sprintf("/api/roles/%s", id), &item)
	return &item, err
}

func (s *RoleService) Create(ctx context.Context, input *models.RoleCreate) (*models.Role, error) {
	var item models.Role
	err := s.client.Post(ctx, "/api/roles", input, &item)
	return &item, err
}

func (s *RoleService) Update(ctx context.Context, id string, input *models.RoleCreate) (*models.Role, error) {
	var item models.Role
	err := s.client.Put(ctx, fmt.Sprintf("/api/roles/%s", id), input, &item)
	return &item, err
}

func (s *RoleService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/roles/%s", id))
}
