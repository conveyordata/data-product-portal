package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type UserService struct {
	client *client.Client
}

func NewUserService(c *client.Client) *UserService {
	return &UserService{client: c}
}

func (s *UserService) List(ctx context.Context) ([]models.User, error) {
	var items []models.User
	err := s.client.Get(ctx, "/api/users", &items)
	return items, err
}

func (s *UserService) Get(ctx context.Context, id string) (*models.User, error) {
	var item models.User
	err := s.client.Get(ctx, fmt.Sprintf("/api/users/%s", id), &item)
	return &item, err
}
