package sdk

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/data-product-portal/sdk-go/models"
)

const (
	defaultBaseURL = "http://localhost:5050"
	defaultAPIKey  = "test-api-key"
)

func getBaseURL() string {
	if url := os.Getenv("SDK_TEST_BASE_URL"); url != "" {
		return url
	}
	return defaultBaseURL
}

func getAPIKey() string {
	if key := os.Getenv("SDK_TEST_API_KEY"); key != "" {
		return key
	}
	return defaultAPIKey
}

func newTestSDK() *DataProductPortalSDK {
	return New(getBaseURL(), getAPIKey())
}

func TestNew(t *testing.T) {
	sdk := New("http://localhost:5050", "test-key")
	if sdk == nil {
		t.Fatal("expected SDK to be non-nil")
	}
	if sdk.Domains == nil {
		t.Error("expected Domains service to be initialized")
	}
	if sdk.DataProducts == nil {
		t.Error("expected DataProducts service to be initialized")
	}
	if sdk.Datasets == nil {
		t.Error("expected Datasets service to be initialized")
	}
	if sdk.Environments == nil {
		t.Error("expected Environments service to be initialized")
	}
	if sdk.Tags == nil {
		t.Error("expected Tags service to be initialized")
	}
	if sdk.Users == nil {
		t.Error("expected Users service to be initialized")
	}
}

// Integration tests - require running backend
// Run with: go test -v (without -short flag)
// Skip with: go test -v -short

func TestDomains_List_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	domains, err := sdk.Domains.List(ctx)
	if err != nil {
		t.Fatalf("failed to list domains: %v", err)
	}

	if len(domains) == 0 {
		t.Log("no domains found (may be expected for empty database)")
	}

	for _, d := range domains {
		if d.ID == "" {
			t.Error("domain ID should not be empty")
		}
		if d.Name == "" {
			t.Error("domain name should not be empty")
		}
	}
	t.Logf("found %d domains", len(domains))
}

func TestDomains_CRUD_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Create
	createInput := &models.DomainCreate{
		Name:        "Test Domain SDK",
		Description: "Created by Go SDK test",
	}

	created, err := sdk.Domains.Create(ctx, createInput)
	if err != nil {
		t.Fatalf("failed to create domain: %v", err)
	}

	if created.ID == "" {
		t.Error("created domain should have an ID")
	}

	// Get
	fetched, err := sdk.Domains.Get(ctx, created.ID)
	if err != nil {
		t.Fatalf("failed to get domain: %v", err)
	}

	if fetched.ID != created.ID {
		t.Errorf("expected ID %q, got %q", created.ID, fetched.ID)
	}
	if fetched.Name != createInput.Name {
		t.Errorf("expected name %q, got %q", createInput.Name, fetched.Name)
	}

	// Update
	updateInput := &models.DomainCreate{
		Name:        "Updated Test Domain SDK",
		Description: "Updated by Go SDK test",
	}

	_, err = sdk.Domains.Update(ctx, created.ID, updateInput)
	if err != nil {
		t.Fatalf("failed to update domain: %v", err)
	}

	// Verify update
	fetchedUpdated, err := sdk.Domains.Get(ctx, created.ID)
	if err != nil {
		t.Fatalf("failed to get updated domain: %v", err)
	}
	if fetchedUpdated.Name != updateInput.Name {
		t.Errorf("expected updated name %q, got %q", updateInput.Name, fetchedUpdated.Name)
	}

	// Delete
	err = sdk.Domains.Delete(ctx, created.ID)
	if err != nil {
		t.Fatalf("failed to delete domain: %v", err)
	}

	// Verify deletion
	_, err = sdk.Domains.Get(ctx, created.ID)
	if err == nil {
		t.Error("expected error when getting deleted domain")
	}
}

func TestTags_List_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	tags, err := sdk.Tags.List(ctx)
	if err != nil {
		t.Fatalf("failed to list tags: %v", err)
	}

	t.Logf("found %d tags", len(tags))
}

func TestUsers_List_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	users, err := sdk.Users.List(ctx)
	if err != nil {
		t.Fatalf("failed to list users: %v", err)
	}

	t.Logf("found %d users", len(users))
}

func TestDatasets_List_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	datasets, err := sdk.Datasets.List(ctx)
	if err != nil {
		t.Fatalf("failed to list datasets: %v", err)
	}

	t.Logf("found %d datasets", len(datasets))
}

func TestPlatforms_List_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	sdk := newTestSDK()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	platforms, err := sdk.Platforms.List(ctx)
	if err != nil {
		t.Fatalf("failed to list platforms: %v", err)
	}

	t.Logf("found %d platforms", len(platforms))
}
