package services

import (
	"context"
	"fmt"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

type DomainService struct {
	client *client.Client
}

func NewDomainService(c *client.Client) *DomainService {
	return &DomainService{client: c}
}

func (s *DomainService) List(ctx context.Context) ([]models.Domain, error) {
	var domains []models.Domain
	err := s.client.Get(ctx, "/api/domains", &domains)
	return domains, err
}

func (s *DomainService) Get(ctx context.Context, id string) (*models.Domain, error) {
	var domain models.Domain
	err := s.client.Get(ctx, fmt.Sprintf("/api/domains/%s", id), &domain)
	return &domain, err
}

func (s *DomainService) Create(ctx context.Context, input *models.DomainCreate) (*models.Domain, error) {
	var domain models.Domain
	err := s.client.Post(ctx, "/api/domains", input, &domain)
	return &domain, err
}

func (s *DomainService) Update(ctx context.Context, id string, input *models.DomainCreate) (*models.Domain, error) {
	var domain models.Domain
	err := s.client.Put(ctx, fmt.Sprintf("/api/domains/%s", id), input, &domain)
	return &domain, err
}

func (s *DomainService) Delete(ctx context.Context, id string) error {
	return s.client.Delete(ctx, fmt.Sprintf("/api/domains/%s", id))
}
