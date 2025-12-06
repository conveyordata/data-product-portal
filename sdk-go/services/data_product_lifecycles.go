package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DataProductLifecycleService struct {
	client *client.Client
}

func NewDataProductLifecycleService(c *client.Client) *DataProductLifecycleService {
	return &DataProductLifecycleService{client: c}
}

func (s *DataProductLifecycleService) List(ctx context.Context) ([]models.DataProductLifecycle, error) {
	var items []models.DataProductLifecycle
	err := s.client.Get(ctx, "/api/data-product-lifecycles", &items)
	return items, err
}

func (s *DataProductLifecycleService) Get(ctx context.Context, id string) (*models.DataProductLifecycle, error) {
	var item models.DataProductLifecycle
	err := s.client.Get(ctx, fmt.Sprintf("/api/data-product-lifecycles/%s", id), &item)
	return &item, err
}

func (s *DataProductLifecycleService) Create(ctx context.Context, input *models.DataProductLifecycleCreate) (*models.DataProductLifecycle, error) {
	var item models.DataProductLifecycle
	err := s.client.Post(ctx, "/api/data-product-lifecycles", input, &item)
	return &item, err
}

func (s *DataProductLifecycleService) Update(ctx context.Context, id string, input *models.DataProductLifecycleCreate) (*models.DataProductLifecycle, error) {
	var item models.DataProductLifecycle
	err := s.client.Put(ctx, fmt.Sprintf("/api/data-product-lifecycles/%s", id), input, &item)
	return &item, err
}

func (s *DataProductLifecycleService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/data-product-lifecycles/%s", id))
}
