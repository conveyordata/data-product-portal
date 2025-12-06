package models

type DataProductLifecycle struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Order int    `json:"order"`
}

type DataProductLifecycleCreate struct {
	Name  string `json:"name"`
	Order int    `json:"order"`
}
