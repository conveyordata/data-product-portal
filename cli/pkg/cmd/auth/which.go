package auth

import (
	"fmt"

	"github.com/spf13/cobra"

	"portal/libs/core"
)

var whichCmd = &cobra.Command{
	Use:   "which",
	Short: "Print the current profile",
	Long:  `This command prints the name of the current profile of the currently logged in user.`,
	Run: func(cmd *cobra.Command, _ []string) {
		profile := core.GetActiveProfile()
		fmt.Printf("Active profile is '%s'\n", profile)
	},
}

func init() {
	Cmd.AddCommand(whichCmd)
}
