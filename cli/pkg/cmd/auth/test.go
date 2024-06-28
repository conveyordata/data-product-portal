package auth

import (
	"github.com/spf13/cobra"

	"portal/libs/test"
)

var testCommand = &cobra.Command{
	Use:   "test",
	Short: "Test auth flow with API",
	RunE: func(cmd *cobra.Command, _ []string) error {
		_, err := test.TestApi(cmd.Context())
		if err != nil {
			return err
		}
		return err
	},
}

func init() {
	Cmd.AddCommand(testCommand)
}
