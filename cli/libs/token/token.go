package token

import (
	"time"

	"github.com/golang-jwt/jwt/v4"
	"github.com/pkg/errors"
)

type Token struct {
	RefreshToken string `json:"refresh_token"`
	AccessToken  string `json:"access_token"`
	Scope        string `json:"scope"`
	ExpiresIn    int    `json:"expires_in"`
	TokenType    string `json:"token_type"`
}

func CheckIfTokenNeedsRefresh(token *Token) (bool, error) {
	if token.AccessToken == "" {
		return true, nil
	}
	parser := jwt.NewParser(jwt.WithJSONNumber())
	var claims jwt.RegisteredClaims
	_, _, err := parser.ParseUnverified(token.AccessToken, &claims)
	if err != nil {
		return true, errors.Wrap(err, "Failed parsing the token")
	}
	// Refresh 10 minutes before expiry
	if claims.ExpiresAt.Time.Before(time.Now().Add(10 * time.Minute)) {
		return true, nil
	}

	return false, nil
}
