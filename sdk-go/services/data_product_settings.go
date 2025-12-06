package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DataProductSettingService struct {
	client *client.Client
}

func NewDataProductSettingService(c *client.Client) *DataProductSettingService {
	return &DataProductSettingService{client: c}
}

func (s *DataProductSettingService) List(ctx context.Context) ([]models.DataProductSetting, error) {
	var items []models.DataProductSetting
	err := s.client.Get(ctx, "/api/data-product-settings", &items)
	return items, err
}

func (s *DataProductSettingService) Get(ctx context.Context, id string) (*models.DataProductSetting, error) {
	var item models.DataProductSetting
	err := s.client.Get(ctx, fmt.Sprintf("/api/data-product-settings/%s", id), &item)
	return &item, err
}

func (s *DataProductSettingService) Create(ctx context.Context, input *models.DataProductSettingCreate) (*models.DataProductSetting, error) {
	var item models.DataProductSetting
	err := s.client.Post(ctx, "/api/data-product-settings", input, &item)
	return &item, err
}

func (s *DataProductSettingService) Update(ctx context.Context, id string, input *models.DataProductSettingCreate) (*models.DataProductSetting, error) {
	var item models.DataProductSetting
	err := s.client.Put(ctx, fmt.Sprintf("/api/data-product-settings/%s", id), input, &item)
	return &item, err
}

func (s *DataProductSettingService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/data-product-settings/%s", id))
}
