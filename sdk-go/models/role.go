package models

type Role struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	Scope       string `json:"scope"`
}

type RoleCreate struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	Scope       string `json:"scope"`
}

type RoleAssignment struct {
	ID       string `json:"id"`
	UserID   string `json:"user_id"`
	RoleID   string `json:"role_id"`
	Scope    string `json:"scope"`
	ScopeID  string `json:"scope_id,omitempty"`
}

type RoleAssignmentCreate struct {
	UserID  string `json:"user_id"`
	RoleID  string `json:"role_id"`
	Scope   string `json:"scope"`
	ScopeID string `json:"scope_id,omitempty"`
}
