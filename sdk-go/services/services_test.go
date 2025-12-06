package services

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/data-product-portal/sdk-go/client"
	"github.com/data-product-portal/sdk-go/models"
)

func newTestClient(handler http.HandlerFunc) *client.Client {
	server := httptest.NewServer(handler)
	return client.NewClient(server.URL, "test-key")
}

func TestDomainService_List(t *testing.T) {
	expectedDomains := []models.Domain{
		{ID: "1", Name: "Domain 1", Description: "First domain"},
		{ID: "2", Name: "Domain 2", Description: "Second domain"},
	}

	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			t.Errorf("expected GET, got %s", r.Method)
		}
		if r.URL.Path != "/api/domains" {
			t.Errorf("expected path /api/domains, got %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(expectedDomains)
	})

	service := NewDomainService(c)
	domains, err := service.List(context.Background())

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(domains) != 2 {
		t.Errorf("expected 2 domains, got %d", len(domains))
	}
	if domains[0].Name != "Domain 1" {
		t.Errorf("expected name 'Domain 1', got %q", domains[0].Name)
	}
}

func TestDomainService_Get(t *testing.T) {
	expectedDomain := models.Domain{ID: "test-id", Name: "Test Domain", Description: "A test domain"}

	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			t.Errorf("expected GET, got %s", r.Method)
		}
		if r.URL.Path != "/api/domains/test-id" {
			t.Errorf("expected path /api/domains/test-id, got %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(expectedDomain)
	})

	service := NewDomainService(c)
	domain, err := service.Get(context.Background(), "test-id")

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if domain.ID != "test-id" {
		t.Errorf("expected ID 'test-id', got %q", domain.ID)
	}
	if domain.Name != "Test Domain" {
		t.Errorf("expected name 'Test Domain', got %q", domain.Name)
	}
}

func TestDomainService_Create(t *testing.T) {
	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if r.URL.Path != "/api/domains" {
			t.Errorf("expected path /api/domains, got %s", r.URL.Path)
		}

		var input models.DomainCreate
		json.NewDecoder(r.Body).Decode(&input)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(models.Domain{
			ID:          "new-id",
			Name:        input.Name,
			Description: input.Description,
		})
	})

	service := NewDomainService(c)
	input := &models.DomainCreate{Name: "New Domain", Description: "A new domain"}
	domain, err := service.Create(context.Background(), input)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if domain.ID != "new-id" {
		t.Errorf("expected ID 'new-id', got %q", domain.ID)
	}
	if domain.Name != "New Domain" {
		t.Errorf("expected name 'New Domain', got %q", domain.Name)
	}
}

func TestDomainService_Update(t *testing.T) {
	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPut {
			t.Errorf("expected PUT, got %s", r.Method)
		}
		if r.URL.Path != "/api/domains/update-id" {
			t.Errorf("expected path /api/domains/update-id, got %s", r.URL.Path)
		}

		var input models.DomainCreate
		json.NewDecoder(r.Body).Decode(&input)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(models.Domain{
			ID:          "update-id",
			Name:        input.Name,
			Description: input.Description,
		})
	})

	service := NewDomainService(c)
	input := &models.DomainCreate{Name: "Updated Domain", Description: "An updated domain"}
	domain, err := service.Update(context.Background(), "update-id", input)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if domain.Name != "Updated Domain" {
		t.Errorf("expected name 'Updated Domain', got %q", domain.Name)
	}
}

func TestDomainService_Delete(t *testing.T) {
	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodDelete {
			t.Errorf("expected DELETE, got %s", r.Method)
		}
		if r.URL.Path != "/api/domains/delete-id" {
			t.Errorf("expected path /api/domains/delete-id, got %s", r.URL.Path)
		}
		w.WriteHeader(http.StatusNoContent)
	})

	service := NewDomainService(c)
	err := service.Delete(context.Background(), "delete-id")

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestTagService_List(t *testing.T) {
	expectedTags := []models.Tag{
		{ID: "1", Value: "tag1"},
		{ID: "2", Value: "tag2"},
	}

	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/tags" {
			t.Errorf("expected path /api/tags, got %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(expectedTags)
	})

	service := NewTagService(c)
	tags, err := service.List(context.Background())

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(tags) != 2 {
		t.Errorf("expected 2 tags, got %d", len(tags))
	}
}

func TestEnvironmentService_List(t *testing.T) {
	expectedEnvs := []models.Environment{
		{ID: "1", Name: "development", Acronym: "dev", Context: "dev_ctx"},
		{ID: "2", Name: "production", Acronym: "prd", Context: "prd_ctx"},
	}

	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/envs" {
			t.Errorf("expected path /api/envs, got %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(expectedEnvs)
	})

	service := NewEnvironmentService(c)
	envs, err := service.List(context.Background())

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(envs) != 2 {
		t.Errorf("expected 2 environments, got %d", len(envs))
	}
}

func TestEnvironmentService_CRUD(t *testing.T) {
	var lastPath string
	var lastMethod string

	c := newTestClient(func(w http.ResponseWriter, r *http.Request) {
		lastPath = r.URL.Path
		lastMethod = r.Method
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(models.Environment{ID: "env-id", Name: "test-env", Acronym: "tst", Context: "test_ctx"})
	})

	service := NewEnvironmentService(c)

	// Test Get
	_, err := service.Get(context.Background(), "env-id")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if lastPath != "/api/envs/env-id" {
		t.Errorf("expected path /api/envs/env-id, got %s", lastPath)
	}
	if lastMethod != http.MethodGet {
		t.Errorf("expected GET, got %s", lastMethod)
	}

	// Test Create
	_, err = service.Create(context.Background(), &models.EnvironmentCreate{Name: "new-env", Acronym: "new", Context: "new_ctx"})
	if err != nil {
		t.Fatalf("Create failed: %v", err)
	}
	if lastPath != "/api/envs" {
		t.Errorf("expected path /api/envs, got %s", lastPath)
	}
	if lastMethod != http.MethodPost {
		t.Errorf("expected POST, got %s", lastMethod)
	}

	// Test Update
	_, err = service.Update(context.Background(), "env-id", &models.EnvironmentCreate{Name: "updated-env", Acronym: "upd", Context: "upd_ctx"})
	if err != nil {
		t.Fatalf("Update failed: %v", err)
	}
	if lastPath != "/api/envs/env-id" {
		t.Errorf("expected path /api/envs/env-id, got %s", lastPath)
	}
	if lastMethod != http.MethodPut {
		t.Errorf("expected PUT, got %s", lastMethod)
	}
}
