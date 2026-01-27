package cognitotoken

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"

	httpclient "portal/libs/httpclient"
	"portal/libs/token"
)

type TokenRequest struct {
	ClientID     string
	ClientSecret string
	AuthUrl      string
	RefreshToken string
}

func FetchToken(ctx context.Context, client httpclient.HTTPClient, request TokenRequest) (*token.Token, error) {
	// getting cognito domain
	req, err := http.NewRequestWithContext(ctx, "GET", fmt.Sprintf("%s/.well-known/openid-configuration", request.AuthUrl), nil)
	if err != nil {
		return nil, fmt.Errorf("failed creating the cognito request: %w", err)
	}

	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	res, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed fetching cognito token: %w", err)
	}
	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}
	var domain struct {
		TokenEndpoint string `json:"token_endpoint"`
	}
	if err := json.Unmarshal(body, &domain); err != nil {
		return nil, fmt.Errorf("failed unmarshalling the token from body: %s: %w", string(body), err)
	}

	data := url.Values{}
	data.Set("grant_type", "refresh_token")
	data.Set("refresh_token", request.RefreshToken)
	req, err = http.NewRequestWithContext(ctx, "POST", domain.TokenEndpoint, strings.NewReader(data.Encode()))
	if err != nil {
		return nil, fmt.Errorf("failed creating the cognito request: %w", err)
	}

	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Add("Content-Length", strconv.Itoa(len(data.Encode())))
	usernamePW := base64.StdEncoding.EncodeToString([]byte(fmt.Sprintf("%s:%s", request.ClientID, request.ClientSecret)))
	req.Header.Add("authorization", fmt.Sprintf("Basic %s", usernamePW))
	res, err = client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed fetching cognito token: %w", err)
	}
	defer res.Body.Close()
	tokenBody, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}
	if res.StatusCode != 200 {
		return nil, fmt.Errorf("unable to fetch the token from cognito: %s", string(tokenBody))
	}

	var t token.Token
	if err := json.Unmarshal(tokenBody, &t); err != nil {
		return nil, fmt.Errorf("failed unmarshalling the token from body: %s: %w", string(tokenBody), err)
	}
	return &t, err
}
