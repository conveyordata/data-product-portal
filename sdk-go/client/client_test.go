package client

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestNewClient(t *testing.T) {
	c := NewClient("http://localhost:5050", "test-key")

	if c.BaseURL != "http://localhost:5050" {
		t.Errorf("expected BaseURL %q, got %q", "http://localhost:5050", c.BaseURL)
	}
	if c.APIKey != "test-key" {
		t.Errorf("expected APIKey %q, got %q", "test-key", c.APIKey)
	}
	if c.HTTPClient == nil {
		t.Error("expected HTTPClient to be non-nil")
	}
}

func TestNewClient_WithHTTPClient(t *testing.T) {
	customClient := &http.Client{Timeout: 60 * time.Second}
	c := NewClient("http://localhost:5050", "test-key", WithHTTPClient(customClient))

	if c.HTTPClient != customClient {
		t.Error("expected custom HTTP client to be set")
	}
}

func TestClient_Get(t *testing.T) {
	type testResponse struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			t.Errorf("expected GET method, got %s", r.Method)
		}
		if r.URL.Path != "/api/test" {
			t.Errorf("expected path /api/test, got %s", r.URL.Path)
		}
		if r.Header.Get("X-API-Key") != "test-key" {
			t.Errorf("expected API key header to be set")
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(testResponse{ID: "123", Name: "Test"})
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx := context.Background()

	var result testResponse
	err := c.Get(ctx, "/api/test", &result)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.ID != "123" {
		t.Errorf("expected ID %q, got %q", "123", result.ID)
	}
	if result.Name != "Test" {
		t.Errorf("expected Name %q, got %q", "Test", result.Name)
	}
}

func TestClient_Post(t *testing.T) {
	type testRequest struct {
		Name string `json:"name"`
	}
	type testResponse struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST method, got %s", r.Method)
		}
		if r.Header.Get("Content-Type") != "application/json" {
			t.Errorf("expected Content-Type application/json")
		}

		var req testRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Fatalf("failed to decode request body: %v", err)
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(testResponse{ID: "456", Name: req.Name})
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx := context.Background()

	var result testResponse
	err := c.Post(ctx, "/api/test", &testRequest{Name: "NewItem"}, &result)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.ID != "456" {
		t.Errorf("expected ID %q, got %q", "456", result.ID)
	}
	if result.Name != "NewItem" {
		t.Errorf("expected Name %q, got %q", "NewItem", result.Name)
	}
}

func TestClient_Put(t *testing.T) {
	type testRequest struct {
		Name string `json:"name"`
	}
	type testResponse struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPut {
			t.Errorf("expected PUT method, got %s", r.Method)
		}

		var req testRequest
		json.NewDecoder(r.Body).Decode(&req)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(testResponse{ID: "789", Name: req.Name})
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx := context.Background()

	var result testResponse
	err := c.Put(ctx, "/api/test/789", &testRequest{Name: "UpdatedItem"}, &result)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if result.Name != "UpdatedItem" {
		t.Errorf("expected Name %q, got %q", "UpdatedItem", result.Name)
	}
}

func TestClient_Delete(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodDelete {
			t.Errorf("expected DELETE method, got %s", r.Method)
		}
		w.WriteHeader(http.StatusNoContent)
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx := context.Background()

	err := c.Delete(ctx, "/api/test/123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestClient_ErrorResponse(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte(`{"error": "not found"}`))
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx := context.Background()

	var result interface{}
	err := c.Get(ctx, "/api/test", &result)
	if err == nil {
		t.Fatal("expected error for 404 response")
	}

	expectedErrMsg := `API error (status 404): {"error": "not found"}`
	if err.Error() != expectedErrMsg {
		t.Errorf("expected error %q, got %q", expectedErrMsg, err.Error())
	}
}

func TestClient_ContextCancellation(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(100 * time.Millisecond)
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	c := NewClient(server.URL, "test-key")
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	var result interface{}
	err := c.Get(ctx, "/api/test", &result)
	if err == nil {
		t.Fatal("expected error for cancelled context")
	}
}
