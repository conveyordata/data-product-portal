package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DataProductService struct {
	client *client.Client
}

func NewDataProductService(c *client.Client) *DataProductService {
	return &DataProductService{client: c}
}

func (s *DataProductService) List(ctx context.Context) ([]models.DataProduct, error) {
	var dataProducts []models.DataProduct
	err := s.client.Get(ctx, "/api/data-products", &dataProducts)
	return dataProducts, err
}

func (s *DataProductService) Get(ctx context.Context, id string) (*models.DataProduct, error) {
	var dataProduct models.DataProduct
	err := s.client.Get(ctx, fmt.Sprintf("/api/data-products/%s", id), &dataProduct)
	return &dataProduct, err
}

func (s *DataProductService) Create(ctx context.Context, input *models.DataProductCreate) (*models.DataProduct, error) {
	var dataProduct models.DataProduct
	err := s.client.Post(ctx, "/api/data-products", input, &dataProduct)
	return &dataProduct, err
}

func (s *DataProductService) Update(ctx context.Context, id string, input *models.DataProductCreate) (*models.DataProduct, error) {
	var dataProduct models.DataProduct
	err := s.client.Put(ctx, fmt.Sprintf("/api/data-products/%s", id), input, &dataProduct)
	return &dataProduct, err
}

func (s *DataProductService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/data-products/%s", id))
}
