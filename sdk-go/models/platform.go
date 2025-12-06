package models

type Platform struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type PlatformCreate struct {
	Name string `json:"name"`
}
