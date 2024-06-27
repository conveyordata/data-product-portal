package auth

import (
	"portal/libs/core"

	"github.com/spf13/cobra"
)

// switchCmd represents the switch command.
var switchCmd = &cobra.Command{
	Use:   "switch",
	Short: "Switch active profile",
	Long:  "Switches the active authentication configuration.",
	Run: func(cmd *cobra.Command, args []string) {
		core.ChangeActiveProfile(switchProfile)
	},
}

var switchProfile string

func init() {
	Cmd.AddCommand(switchCmd)
	switchCmd.Flags().StringVarP(&switchProfile, "profile", "p", "default", "The profile to switch to")
}
