package models

type DataProductSetting struct {
	ID    string `json:"id"`
	Key   string `json:"key"`
	Value string `json:"value"`
}

type DataProductSettingCreate struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}
