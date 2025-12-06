package models

type Environment struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Acronym   string `json:"acronym"`
	Context   string `json:"context"`
	IsDefault bool   `json:"is_default"`
}

type EnvironmentCreate struct {
	Name    string `json:"name"`
	Acronym string `json:"acronym"`
	Context string `json:"context"`
}
