package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DataProductTypeService struct {
	client *client.Client
}

func NewDataProductTypeService(c *client.Client) *DataProductTypeService {
	return &DataProductTypeService{client: c}
}

func (s *DataProductTypeService) List(ctx context.Context) ([]models.DataProductType, error) {
	var items []models.DataProductType
	err := s.client.Get(ctx, "/api/data-product-types", &items)
	return items, err
}

func (s *DataProductTypeService) Get(ctx context.Context, id string) (*models.DataProductType, error) {
	var item models.DataProductType
	err := s.client.Get(ctx, fmt.Sprintf("/api/data-product-types/%s", id), &item)
	return &item, err
}

func (s *DataProductTypeService) Create(ctx context.Context, input *models.DataProductTypeCreate) (*models.DataProductType, error) {
	var item models.DataProductType
	err := s.client.Post(ctx, "/api/data-product-types", input, &item)
	return &item, err
}

func (s *DataProductTypeService) Update(ctx context.Context, id string, input *models.DataProductTypeCreate) (*models.DataProductType, error) {
	var item models.DataProductType
	err := s.client.Put(ctx, fmt.Sprintf("/api/data-product-types/%s", id), input, &item)
	return &item, err
}

func (s *DataProductTypeService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/data-product-types/%s", id))
}
