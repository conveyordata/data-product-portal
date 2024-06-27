package auth

import (
	"github.com/spf13/cobra"
	//"fmt"
	"portal/libs/auth"
)

var loginCommand = &cobra.Command{
	Use:   "login",
	Short: "Login flow to get a new token",
	RunE: func(cmd *cobra.Command, _ []string) error {
		_, err := auth.Login(cmd.Context())
		return err
	},
}

func init() {
	Cmd.AddCommand(loginCommand)
}
