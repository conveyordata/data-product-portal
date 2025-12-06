package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type ThemeSettingService struct {
	client *client.Client
}

func NewThemeSettingService(c *client.Client) *ThemeSettingService {
	return &ThemeSettingService{client: c}
}

func (s *ThemeSettingService) List(ctx context.Context) ([]models.ThemeSetting, error) {
	var items []models.ThemeSetting
	err := s.client.Get(ctx, "/api/theme-settings", &items)
	return items, err
}

func (s *ThemeSettingService) Get(ctx context.Context, id string) (*models.ThemeSetting, error) {
	var item models.ThemeSetting
	err := s.client.Get(ctx, fmt.Sprintf("/api/theme-settings/%s", id), &item)
	return &item, err
}

func (s *ThemeSettingService) Update(ctx context.Context, id string, input *models.ThemeSettingCreate) (*models.ThemeSetting, error) {
	var item models.ThemeSetting
	err := s.client.Put(ctx, fmt.Sprintf("/api/theme-settings/%s", id), input, &item)
	return &item, err
}
