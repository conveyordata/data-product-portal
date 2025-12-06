package models

type DataProduct struct {
	ID          string  `json:"id"`
	Name        string  `json:"name"`
	Description string  `json:"description"`
	About       *string `json:"about,omitempty"`
	Namespace   string  `json:"namespace"`
	Status      string  `json:"status"`
	DomainID    string  `json:"domain_id"`
	TypeID      string  `json:"type_id"`
}

type DataProductCreate struct {
	Name        string  `json:"name"`
	Description string  `json:"description"`
	About       *string `json:"about,omitempty"`
	DomainID    string  `json:"domain_id"`
	TypeID      string  `json:"type_id"`
}
