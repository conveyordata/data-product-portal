package models

type DataProductType struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	IconKey string `json:"icon_key"`
}

type DataProductTypeCreate struct {
	Name    string `json:"name"`
	IconKey string `json:"icon_key"`
}
