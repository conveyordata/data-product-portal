package cmds

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"os"
	"portal/libs/cliapi"
	"portal/libs/core"
	"portal/pkg/api"
	"time"
)

type AWSCredentials struct {
	Version         int    `json:"Version"`
	AccessKeyId     string `json:"AccessKeyId"`
	SecretAccessKey string `json:"SecretAccessKey"`
	SessionToken    string `json:"SessionToken"`
	Expiration      string `json:"Expiration"`
}

func OpenAPIAws(ctx context.Context, data_product string, environment string) (*AWSCredentials, error) {
	client, err := cliapi.AuthenticatedContext(ctx)
	if err != nil {
		return nil, err
	}
	params := api.GetAwsCredentialsApiAuthAwsCredentialsGetParams{DataProductName: data_product, Environment: environment}
	resp, err := client.GetAwsCredentialsApiAuthAwsCredentialsGet(ctx, &params)
	if err != nil {
		return nil, err
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var cred AWSCredentials
	err = json.Unmarshal(body, &cred)
	cred.Version = 1
	if err != nil {
		return nil, err
	}

	err = WriteAWSToken(&cred, data_product+environment)
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()

	return &cred, nil
}

func GetAWSRole(ctx context.Context, data_product string, environment string) (*AWSCredentials, error) {
	catched_cred, err := ReadAWSToken(data_product+environment)
	switch {
	case errors.Is(err, core.ErrTokenDoesNotExist):
		// Generate new credentials
		return OpenAPIAws(ctx, data_product, environment)
	case err != nil:
		return nil, err
	default:
		// Return cred if not expired else generate new creds
		const layout = "2006-01-02T15:04:05Z"
		expiration, err := time.Parse(layout, catched_cred.Expiration)

		if err != nil {
			return OpenAPIAws(ctx, data_product, environment)
		}
		if expiration.Before(time.Now().UTC()) {
			return OpenAPIAws(ctx, data_product, environment)
		}

		return catched_cred, err
	}
}

func WriteAWSToken(token *AWSCredentials, activeProfile string) error {
	core.EnsureConfigDirectoryExists()
	core.EnsureAWSTokenDirectoryExists()
	tokenFile := core.AwsTokenFileLocation(activeProfile)
	tokenJson, err := json.Marshal(token)
	if err != nil {
		return err
	}
	return os.WriteFile(tokenFile, tokenJson, 0644)
}

func ReadAWSToken(activeProfile string) (*AWSCredentials, error) {
	bytes, err := os.ReadFile(core.AwsTokenFileLocation(activeProfile))
	if err != nil && os.IsNotExist(err) {
		return nil, core.ErrTokenDoesNotExist
	}
	if err != nil {
		return nil, err
	}
	var t AWSCredentials
	if err := json.Unmarshal(bytes, &t); err != nil {
		return nil, err
	}
	return &t, nil
}
