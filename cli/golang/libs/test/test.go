package test

import (
	"context"
	"fmt"

	"portal/libs/cliapi"
)

func TestApi(ctx context.Context) (bool, error) {
	client, err := cliapi.AuthenticatedContext(ctx)
	if err != nil {
		return false, err
	}
	resp, err := client.AuthorizeApiAuthUserGet(ctx)
	if err != nil {
		return false, err
	}

	if resp.StatusCode == 200 {
		fmt.Println("CLI is correctly authenticated")
		return true, nil
	} else {
		fmt.Println("CLI is not authenticated")
		return false, nil
	}
}
