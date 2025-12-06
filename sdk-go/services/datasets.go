package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DatasetService struct {
	client *client.Client
}

func NewDatasetService(c *client.Client) *DatasetService {
	return &DatasetService{client: c}
}

func (s *DatasetService) List(ctx context.Context) ([]models.Dataset, error) {
	var datasets []models.Dataset
	err := s.client.Get(ctx, "/api/datasets", &datasets)
	return datasets, err
}

func (s *DatasetService) Get(ctx context.Context, id string) (*models.Dataset, error) {
	var dataset models.Dataset
	err := s.client.Get(ctx, fmt.Sprintf("/api/datasets/%s", id), &dataset)
	return &dataset, err
}

func (s *DatasetService) Create(ctx context.Context, input *models.DatasetCreate) (*models.Dataset, error) {
	var dataset models.Dataset
	err := s.client.Post(ctx, "/api/datasets", input, &dataset)
	return &dataset, err
}

func (s *DatasetService) Update(ctx context.Context, id string, input *models.DatasetCreate) (*models.Dataset, error) {
	var dataset models.Dataset
	err := s.client.Put(ctx, fmt.Sprintf("/api/datasets/%s", id), input, &dataset)
	return &dataset, err
}

func (s *DatasetService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/datasets/%s", id))
}
