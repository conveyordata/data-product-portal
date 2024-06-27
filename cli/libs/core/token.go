package core

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"os"
	"path/filepath"
	utils "portal/libs/httpclient"
	"portal/libs/logger"
	"portal/libs/token"
	"portal/libs/token/cognitotoken"
	"strings"
)

var (
	ErrTokenDoesNotExist = errors.New("token does not exist")
)

func FetchToken(ctx context.Context) (*token.Token, error) {
	activeProfile := GetActiveProfile()
	t, err := ReadToken(activeProfile)
	client := http.DefaultClient
	switch {
	case err != nil:
		return nil, err
	default:
		refresh, err := token.CheckIfTokenNeedsRefresh(t)
		if err != nil {
			return nil, err
		}
		if refresh {
			logger.Debugf("Token is expired")

			return fetchAndSetFreshToken(ctx, activeProfile, client, t)
		}
		return t, nil
	}
}

func fetchAndSetFreshToken(ctx context.Context, activeProfile string, client utils.HTTPClient, token *token.Token) (*token.Token, error) {
	config := GetCurrentConfig()
	// Trigger login flow when key and secret are empty since clientID is always filled in
	// if config.Key == "" && config.Secret == "" && config.ClientID != "" {
	// 	return Login(ctx)
	// }
	// Otherwise trigger M2M fetching
	t, err := fetchFreshM2MToken(ctx, config, client, token)
	if err != nil {
		return nil, err
	}
	token.AccessToken = t.AccessToken
	err = WriteToken(token, activeProfile)
	if err != nil {
		return nil, err
	}
	return t, nil
}

func fetchFreshM2MToken(ctx context.Context, config Config, client utils.HTTPClient, token *token.Token) (*token.Token, error) {
	// if strings.Contains(config.Auth, "auth0.com") || config.Auth == DefaultAuth {
	// 	audience := config.Audience
	// 	audience = strings.Replace(audience, "app.", "api.", 1)
	// 	auth := config.Auth
	// 	if config.Auth == DefaultAuth {
	// 		auth = OldDefaultAuth
	// 	}
	// 	t, err := auth0token.FetchToken(ctx, auth0token.TokenRequest{
	// 		GrantType:    "client_credentials",
	// 		ClientID:     config.ClientID,
	// 		ClientSecret: config.Secret,
	// 		Audience:     audience,
	// 	}, auth, client)
	// 	if err == nil {
	// 		return t, err
	// 	}
	// 	// If the auth is the same as default auth we want to try and see if the key/secret is a cognito token
	// 	if err != nil && config.Auth != DefaultAuth {
	// 		return nil, err
	// 	}
	// }
	return cognitotoken.FetchToken(ctx, client, cognitotoken.TokenRequest{
		ClientID:     config.ClientID,
		ClientSecret: config.Secret,
		AuthUrl:      config.AuthUrl,
		RefreshToken: token.RefreshToken,
	})
}

func tokenBaseLocation() string {
	return filepath.Join(cliLocation(), "tokens")
}

func awsTokenBaseLocation() string {
	return filepath.Join(cliLocation(), "aws")
}

func AwsTokenFileLocation(activeProfile string) string {
	activeProfile = strings.Replace(activeProfile, ":", "-", -1)
	activeProfile = strings.Replace(activeProfile, "/", "-", -1)
	return filepath.Join(awsTokenBaseLocation(), activeProfile)
}

func tokenFileLocation(activeProfile string) string {
	return filepath.Join(tokenBaseLocation(), activeProfile)
}

func ClearToken(activeProfile string) error {
	if err := os.Remove(tokenFileLocation(activeProfile)); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}

func ReadToken(activeProfile string) (*token.Token, error) {
	bytes, err := os.ReadFile(tokenFileLocation(activeProfile))
	if err != nil && os.IsNotExist(err) {
		return nil, ErrTokenDoesNotExist
	}
	if err != nil {
		return nil, err
	}
	var t token.Token
	if err := json.Unmarshal(bytes, &t); err != nil {
		return nil, err
	}
	return &t, nil
}

func ensureTokenDirectoryExists() {
	if _, err := os.Stat(tokenBaseLocation()); os.IsNotExist(err) {
		if err := os.MkdirAll(tokenBaseLocation(), os.ModePerm); err != nil {
			panic(err)
		}
	}
}

func EnsureAWSTokenDirectoryExists() {
	if _, err := os.Stat(awsTokenBaseLocation()); os.IsNotExist(err) {
		if err := os.MkdirAll(awsTokenBaseLocation(), os.ModePerm); err != nil {
			panic(err)
		}
	}
}

func WriteToken(token *token.Token, activeProfile string) error {
	EnsureConfigDirectoryExists()
	ensureTokenDirectoryExists()
	tokenFile := tokenFileLocation(activeProfile)
	tokenJson, err := json.Marshal(token)
	if err != nil {
		return err
	}
	return os.WriteFile(tokenFile, tokenJson, 0644)
}
