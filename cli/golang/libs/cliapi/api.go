package cliapi

import (
	"context"

	"portal/libs/core"
	"portal/pkg/api"
)

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
	client, err := api.NewClient(baseUrl, &basicAuthSource{username: token.AccessToken})
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
