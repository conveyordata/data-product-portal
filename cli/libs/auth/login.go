package auth

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"portal/libs/cliapi"
	"portal/libs/core"
	"portal/libs/token"
	"time"

	"portal/pkg/api"

	"github.com/pkg/browser"
)

func requestJWT(ctx context.Context, config core.Config, device string) (*token.Token, error) {
	client, err := cliapi.BasicAuthenticatedContext()
	if err != nil {
		return nil, err
	}
	params := api.GetJwtTokenApiAuthDeviceJwtTokenPostParams{ClientId: config.ClientID, DeviceCode: device, GrantType: "urn:ietf:params:oauth:grant-type:device_code"}

	resp, err := client.GetJwtTokenApiAuthDeviceJwtTokenPost(ctx, &params)
	if err != nil {
		return nil, err
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()

	var jwtBody token.Token
	err = json.Unmarshal(body, &jwtBody)
	if err != nil {
		return nil, err
	}
	type notFetchedBody struct {
		Detail string `json:"detail"`
	}
	var fullBody notFetchedBody
	err = json.Unmarshal(body, &fullBody)
	if err != nil {
		return nil, err
	}
	if fullBody.Detail == "denied" {
		fmt.Println("Verification request was denied")
		return nil, errors.New("denied")
	}

	return &jwtBody, nil
}

func Login(ctx context.Context) (*token.Token, error) {
	config := core.GetCurrentConfig()
	client, err := cliapi.BasicAuthenticatedContext()
	if err != nil {
		return nil, err
	}

	params := api.GetDeviceTokenApiAuthDeviceDeviceTokenPostParams{ClientId: config.ClientID}

	resp, err := client.GetDeviceTokenApiAuthDeviceDeviceTokenPost(ctx, &params)
	if err != nil {
		return nil, err
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	fmt.Println("Redirecting you to the CLI login page, waiting for automatic authentication...")

	defer resp.Body.Close()

	type TokenBody struct {
		DeviceCode              string `json:"device_code"`
		UserCode                string `json:"user_code"`
		VerificationUri         string `json:"verification_uri"`
		VerificationUriComplete string `json:"verification_uri_complete"`
		Interval                int    `json:"interval"`
		CodeExpiration          int    `json:"code_expiration"`
	}
	var tokenBody TokenBody
	err = json.Unmarshal(body, &tokenBody)
	if err != nil {
		return nil, err
	}
	loginUrl := tokenBody.VerificationUriComplete

	//loginUrl = strings.Replace(loginUrl, config.Api, "http://localhost:5050/", 1)

	if err := browser.OpenURL(loginUrl); err != nil {
		fmt.Println("Could not open the browser automatically, please go to this url: ", loginUrl)
	}

	fmt.Println("Please verify this user code: ", tokenBody.UserCode)
	for {
		select {
		case <-ctx.Done():
			return nil, errors.New("could not authorize the CLI within a minute")
		default:
			time.Sleep(time.Duration(tokenBody.Interval+1) * time.Second)
			t, err := requestJWT(ctx, config, tokenBody.DeviceCode)
			if err != nil {
				return nil, err
			}
			if t.AccessToken != "" {
				return t, core.WriteToken(t, core.GetActiveProfile())
			} else {
				continue
			}
		}
	}
}
