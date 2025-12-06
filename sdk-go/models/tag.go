package models

type Tag struct {
	ID    string `json:"id"`
	Value string `json:"value"`
}

type TagCreate struct {
	Value string `json:"value"`
}
