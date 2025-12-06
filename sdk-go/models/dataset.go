package models

type Dataset struct {
	ID          string  `json:"id"`
	Name        string  `json:"name"`
	Description string  `json:"description,omitempty"`
	DomainID    string  `json:"domain_id"`
}

type DatasetCreate struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	DomainID    string `json:"domain_id"`
}
