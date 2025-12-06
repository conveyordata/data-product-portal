package models

type ThemeSetting struct {
	ID    string `json:"id"`
	Key   string `json:"key"`
	Value string `json:"value"`
}

type ThemeSettingCreate struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}
