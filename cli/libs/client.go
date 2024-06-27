package utils

import "net/http"

type HTTPClient interface {
	Get(url string) (resp *http.Response, err error)
	Do(req *http.Request) (resp *http.Response, err error)
}

var (
	Client HTTPClient
)

func init() {
	Client = http.DefaultClient
}
