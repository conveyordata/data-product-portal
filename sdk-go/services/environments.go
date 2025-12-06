package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type EnvironmentService struct {
	client *client.Client
}

func NewEnvironmentService(c *client.Client) *EnvironmentService {
	return &EnvironmentService{client: c}
}

func (s *EnvironmentService) List(ctx context.Context) ([]models.Environment, error) {
	var items []models.Environment
	err := s.client.Get(ctx, "/api/envs", &items)
	return items, err
}

func (s *EnvironmentService) Get(ctx context.Context, id string) (*models.Environment, error) {
	var item models.Environment
	err := s.client.Get(ctx, fmt.Sprintf("/api/envs/%s", id), &item)
	return &item, err
}

func (s *EnvironmentService) Create(ctx context.Context, input *models.EnvironmentCreate) (*models.Environment, error) {
	var item models.Environment
	err := s.client.Post(ctx, "/api/envs", input, &item)
	return &item, err
}

func (s *EnvironmentService) Update(ctx context.Context, id string, input *models.EnvironmentCreate) (*models.Environment, error) {
	var item models.Environment
	err := s.client.Put(ctx, fmt.Sprintf("/api/envs/%s", id), input, &item)
	return &item, err
}

func (s *EnvironmentService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/envs/%s", id))
}
