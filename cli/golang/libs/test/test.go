package test

import (
	"context"

	"portal/libs/cliapi"
)

func TestApi(ctx context.Context) error {
	client, err := cliapi.AuthenticatedContext(ctx)
	if err != nil {
		return err
	}
	if _, err := client.GetCurrentUser(ctx); err != nil {
		return err
	}
	return nil
}
