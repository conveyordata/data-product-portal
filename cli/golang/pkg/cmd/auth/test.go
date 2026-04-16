package auth

import (
	"github.com/spf13/cobra"

	"portal/libs/test"
)

var testCommand = &cobra.Command{
	Use:   "test",
	Short: "Test auth flow with API",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if err := test.TestApi(cmd.Context()); err != nil {
			return err
		}
		return nil
	},
}

func init() {
	Cmd.AddCommand(testCommand)
}
