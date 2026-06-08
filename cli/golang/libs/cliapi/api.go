package cliapi

import (
	"context"
	"fmt"
	"net/http"

	"portal/libs/core"
	"portal/pkg/api"
)

type bearerTransport struct {
	accessToken string
	base        http.RoundTripper
}

func (t *bearerTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	r := req.Clone(req.Context())
	r.Header.Set("Authorization", fmt.Sprintf("Bearer %s", t.accessToken))
	return t.base.RoundTrip(r)
}

func AuthenticatedContext(ctx context.Context) (api.Invoker, error) {
	token, err := core.FetchToken(ctx)
	if err != nil {
		return nil, err
	}
	config := core.GetCurrentConfig()
	baseUrl := config.Api
	if config.DevMode {
		baseUrl = "http://localhost:5050"
	}
	httpClient := &http.Client{
		Transport: &bearerTransport{
			accessToken: token.AccessToken,
			base:        http.DefaultTransport,
		},
	}
	client, err := api.NewClient(baseUrl, &basicAuthSource{}, api.WithClient(httpClient))
	if err != nil {
		return nil, err
	}
	return client, nil
}

type basicAuthSource struct {
	username, password string
}

func (b *basicAuthSource) HTTPBasic(_ context.Context, _ api.OperationName) (api.HTTPBasic, error) {
	return api.HTTPBasic{Username: b.username, Password: b.password}, nil
}

func BasicAuthenticatedContext() (api.Invoker, error) {
	config := core.GetCurrentConfig()
	baseUrl := config.Api
	if config.DevMode {
		baseUrl = "http://localhost:5050"
	}
	client, err := api.NewClient(baseUrl, &basicAuthSource{username: config.ClientID, password: config.Secret})
	if err != nil {
		return nil, err
	}

	return client, nil
}
