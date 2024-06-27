package auth

import (
	"github.com/spf13/cobra"
)

var Cmd = &cobra.Command{
	Use:   "auth",
	Short: "Auth configuration",
	Long: `Sub commands to configure how to authenticate the CLI.
The authentication settings are by default saved in the ~/.portal directory.
`,
}
