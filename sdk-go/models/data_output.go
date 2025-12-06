package models

type DataOutput struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	Description   string                 `json:"description,omitempty"`
	OwnerID       string                 `json:"owner_id"`
	Configuration map[string]interface{} `json:"configuration"`
}

type DataOutputCreate struct {
	Name          string                 `json:"name"`
	Description   string                 `json:"description,omitempty"`
	OwnerID       string                 `json:"owner_id"`
	Configuration map[string]interface{} `json:"configuration"`
}
