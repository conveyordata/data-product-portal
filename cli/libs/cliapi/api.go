package cliapi

import (
	"context"

	"github.com/deepmap/oapi-codegen/pkg/securityprovider"

	"portal/libs/core"
	"portal/pkg/api"
)

func AuthenticatedContext(ctx context.Context) (api.ClientInterface, error) {
	token, err := core.FetchToken(ctx)
	if err != nil {
		return nil, err
	}
	bearerTokenProvider, err := securityprovider.NewSecurityProviderBearerToken(token.AccessToken)
	if err != nil {
		return nil, err
	}
	config := core.GetCurrentConfig()
	base_url := config.Api
	if config.DevMode {
		base_url = "http://localhost:5050"
	}
	client, err := api.NewClient(base_url, api.WithRequestEditorFn(bearerTokenProvider.Intercept))
	if err != nil {
		return nil, err
	}
	return client, nil
}

func BasicAuthenticatedContext() (api.ClientInterface, error) {
	config := core.GetCurrentConfig()
	bearerTokenProvider, err := securityprovider.NewSecurityProviderBasicAuth(config.ClientID, config.Secret)
	if err != nil {
		return nil, err
	}

	base_url := config.Api
	if config.DevMode {
		base_url = "http://localhost:5050"
	}
	client, err := api.NewClient(base_url, api.WithRequestEditorFn(bearerTokenProvider.Intercept))
	if err != nil {
		return nil, err
	}

	return client, nil
}
