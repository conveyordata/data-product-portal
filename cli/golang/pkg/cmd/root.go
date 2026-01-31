package cmd

import (
	"os"

	"github.com/spf13/cobra"

	"portal/libs/core"
	"portal/pkg/cmd/auth"
)

const version = "1.0"

// rootCmd represents the base command when called without any subcommands.
var rootCmd = &cobra.Command{
	Use:              "data-product-portal",
	Version:          version,
	PersistentPreRun: core.EnsureValidConfig,
	Short:            "A CLI utility for interacting with the data product portal CLI",
	Long: `Data product portal is a portal for managing data products.
  This CLI utility grants users access to the API, for example to gain
  local access to cloud resources.
  `,
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	cobra.OnInitialize(core.InitConfig)
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")

	rootCmd.AddCommand(auth.Cmd)
}
