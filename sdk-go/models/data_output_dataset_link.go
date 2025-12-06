package models

type DataOutputDatasetLink struct {
	ID           string `json:"id"`
	DataOutputID string `json:"data_output_id"`
	DatasetID    string `json:"dataset_id"`
	Status       string `json:"status"`
}

type DataOutputDatasetLinkCreate struct {
	DataOutputID string `json:"data_output_id"`
	DatasetID    string `json:"dataset_id"`
}
