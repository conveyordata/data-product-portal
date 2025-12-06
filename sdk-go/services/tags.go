package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type TagService struct {
	client *client.Client
}

func NewTagService(c *client.Client) *TagService {
	return &TagService{client: c}
}

func (s *TagService) List(ctx context.Context) ([]models.Tag, error) {
	var items []models.Tag
	err := s.client.Get(ctx, "/api/tags", &items)
	return items, err
}

func (s *TagService) Get(ctx context.Context, id string) (*models.Tag, error) {
	var item models.Tag
	err := s.client.Get(ctx, fmt.Sprintf("/api/tags/%s", id), &item)
	return &item, err
}

func (s *TagService) Create(ctx context.Context, input *models.TagCreate) (*models.Tag, error) {
	var item models.Tag
	err := s.client.Post(ctx, "/api/tags", input, &item)
	return &item, err
}

func (s *TagService) Update(ctx context.Context, id string, input *models.TagCreate) (*models.Tag, error) {
	var item models.Tag
	err := s.client.Put(ctx, fmt.Sprintf("/api/tags/%s", id), input, &item)
	return &item, err
}

func (s *TagService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/tags/%s", id))
}
