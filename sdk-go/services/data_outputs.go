package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DataOutputService struct {
	client *client.Client
}

func NewDataOutputService(c *client.Client) *DataOutputService {
	return &DataOutputService{client: c}
}

func (s *DataOutputService) List(ctx context.Context) ([]models.DataOutput, error) {
	var items []models.DataOutput
	err := s.client.Get(ctx, "/api/data-outputs", &items)
	return items, err
}

func (s *DataOutputService) Get(ctx context.Context, id string) (*models.DataOutput, error) {
	var item models.DataOutput
	err := s.client.Get(ctx, fmt.Sprintf("/api/data-outputs/%s", id), &item)
	return &item, err
}

func (s *DataOutputService) Create(ctx context.Context, input *models.DataOutputCreate) (*models.DataOutput, error) {
	var item models.DataOutput
	err := s.client.Post(ctx, "/api/data-outputs", input, &item)
	return &item, err
}

func (s *DataOutputService) Update(ctx context.Context, id string, input *models.DataOutputCreate) (*models.DataOutput, error) {
	var item models.DataOutput
	err := s.client.Put(ctx, fmt.Sprintf("/api/data-outputs/%s", id), input, &item)
	return &item, err
}

func (s *DataOutputService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/data-outputs/%s", id))
}
