package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type RoleAssignmentService struct {
	client *client.Client
}

func NewRoleAssignmentService(c *client.Client) *RoleAssignmentService {
	return &RoleAssignmentService{client: c}
}

func (s *RoleAssignmentService) List(ctx context.Context) ([]models.RoleAssignment, error) {
	var items []models.RoleAssignment
	err := s.client.Get(ctx, "/api/role-assignments", &items)
	return items, err
}

func (s *RoleAssignmentService) Get(ctx context.Context, id string) (*models.RoleAssignment, error) {
	var item models.RoleAssignment
	err := s.client.Get(ctx, fmt.Sprintf("/api/role-assignments/%s", id), &item)
	return &item, err
}

func (s *RoleAssignmentService) Create(ctx context.Context, input *models.RoleAssignmentCreate) (*models.RoleAssignment, error) {
	var item models.RoleAssignment
	err := s.client.Post(ctx, "/api/role-assignments", input, &item)
	return &item, err
}

func (s *RoleAssignmentService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/role-assignments/%s", id))
}
