package models

type DataProductDatasetLink struct {
	ID            string `json:"id"`
	DataProductID string `json:"data_product_id"`
	DatasetID     string `json:"dataset_id"`
	Status        string `json:"status"`
}

type DataProductDatasetLinkCreate struct {
	DataProductID string `json:"data_product_id"`
	DatasetID     string `json:"dataset_id"`
}
