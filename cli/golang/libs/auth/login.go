package auth

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/ogen-go/ogen/validate"
	"github.com/pkg/browser"

	"portal/libs/cliapi"
	"portal/libs/core"
	"portal/libs/errortranslation"
	"portal/libs/token"
	"portal/pkg/api"
)

func requestJWT(ctx context.Context, config core.Config, device string) (*token.Token, error) {
	client, err := cliapi.BasicAuthenticatedContext()
	if err != nil {
		return nil, err
	}
	resp, err := client.GetJwtToken(ctx, api.GetJwtTokenParams{
		ClientID:   config.ClientID,
		DeviceCode: device,
		GrantType:  "urn:ietf:params:oauth:grant-type:device_code",
	})
	if err != nil {
		var statusErr *validate.UnexpectedStatusCodeError
		if errors.As(err, &statusErr) && statusErr.StatusCode == 400 && statusErr.Payload != nil {
			var body struct {
				Detail string `json:"detail"`
			}
			if jsonErr := json.NewDecoder(statusErr.Payload.Body).Decode(&body); jsonErr == nil {
				if body.Detail == "denied" {
					fmt.Println("Verification request was denied")
					return nil, errors.New("denied")
				}
				// authorization_pending or other transient states — signal caller to keep polling
				return nil, nil
			}
		}
		return nil, err
	}

	switch r := resp.(type) {
	case *api.OIDCTokenResponse:
		return &token.Token{
			RefreshToken: r.GetRefreshToken().Value,
			AccessToken:  r.GetAccessToken(),
			ExpiresIn:    r.GetExpiresIn(),
			TokenType:    r.GetTokenType(),
		}, nil
	case *api.HTTPValidationError:
		return nil, errortranslation.TranslateHttpError(r)
	}
	return nil, errors.New("unknown response type")
}

func Login(ctx context.Context) (*token.Token, error) {
	config := core.GetCurrentConfig()
	client, err := cliapi.BasicAuthenticatedContext()
	if err != nil {
		return nil, err
	}

	resp, err := client.GetDeviceToken(ctx, api.GetDeviceTokenParams{
		ClientID: config.ClientID,
	})
	if err != nil {
		return nil, err
	}
	switch r := resp.(type) {
	case *api.HTTPValidationError:
		return nil, errortranslation.TranslateHttpError(r)
	case *api.GetDeviceTokenOKApplicationJSON:
		type TokenBody struct {
			DeviceCode              string `json:"device_code"`
			UserCode                string `json:"user_code"`
			VerificationUri         string `json:"verification_uri"`
			VerificationUriComplete string `json:"verification_uri_complete"`
			Interval                int    `json:"interval"`
			CodeExpiration          int    `json:"code_expiration"`
		}
		var tokenBody TokenBody
		if err := json.Unmarshal(*r, &tokenBody); err != nil {
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
				if t == nil {
					continue
				}
				if t.AccessToken != "" {
					return t, core.WriteToken(t, core.GetActiveProfile())
				} else {
					continue
				}
			}
		}
	}
	return nil, errors.New("unknown response type")
}
