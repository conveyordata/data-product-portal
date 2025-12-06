package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type PlatformService struct {
	client *client.Client
}

func NewPlatformService(c *client.Client) *PlatformService {
	return &PlatformService{client: c}
}

func (s *PlatformService) List(ctx context.Context) ([]models.Platform, error) {
	var items []models.Platform
	err := s.client.Get(ctx, "/api/platforms", &items)
	return items, err
}

func (s *PlatformService) Get(ctx context.Context, id string) (*models.Platform, error) {
	var item models.Platform
	err := s.client.Get(ctx, fmt.Sprintf("/api/platforms/%s", id), &item)
	return &item, err
}

func (s *PlatformService) Create(ctx context.Context, input *models.PlatformCreate) (*models.Platform, error) {
	var item models.Platform
	err := s.client.Post(ctx, "/api/platforms", input, &item)
	return &item, err
}

func (s *PlatformService) Update(ctx context.Context, id string, input *models.PlatformCreate) (*models.Platform, error) {
	var item models.Platform
	err := s.client.Put(ctx, fmt.Sprintf("/api/platforms/%s", id), input, &item)
	return &item, err
}

func (s *PlatformService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/platforms/%s", id))
}
