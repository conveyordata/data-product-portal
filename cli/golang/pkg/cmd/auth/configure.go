package auth

import (
	"github.com/pkg/errors"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"portal/libs/core"
)

// configureCmd represents the configure command.
var configureCmd = &cobra.Command{
	Use:   "configure",
	Short: "Configure the Portal CLI to authenticate yourself",
	Long:  "Configure the Portal CLI to authenticate yourself.",
	Example: `If you want to use OIDC flow, set the following:

$ portal auth configure --key <some_key> --secret <some_secret> --auth <auth_uri> --api <host>

All flags have to be passed at once, you can not call this command multiple times for each config you wan to set.
Since calling this command multiple times will overwrite the configuration every time.
`,
	PreRunE: func(cmd *cobra.Command, args []string) error {
		return validateInput(keyFlag, secretFlag, clientIdFlag)
	},
	Run: func(cmd *cobra.Command, args []string) {
		viper.Set("activeProfile", profileName)
		config := core.DefaultConfig()
		if apiFlag != "" {
			config.Api = apiFlag
		}
		if authFlag != "" {
			config.AuthUrl = authFlag
		}
		if keyFlag != "" && secretFlag != "" {
			config.ClientID = keyFlag
			config.Secret = secretFlag
		}
		core.WriteConfig(config, profileName)
	},
}

func validateInput(keyFlag string, secretFlag string, clientIdFlag string) error {
	if (keyFlag != "" || secretFlag != "") && clientIdFlag != "" {
		return errors.New("You should set either the client id flag for a user flow, or the key and secret for m2m flow")
	}
	if keyFlag != "" && secretFlag == "" || keyFlag == "" && secretFlag != "" {
		return errors.New("For the m2m flow you need both the key and secret set")
	}
	return nil
}

var apiFlag string
var authFlag string
var keyFlag string
var secretFlag string
var profileName string
var clientIdFlag string

func init() {
	Cmd.AddCommand(configureCmd)

	configureCmd.Flags().StringVar(&apiFlag, "api", "", "The portal api to connect to")
	configureCmd.Flags().StringVar(&authFlag, "auth", "", "The portal auth url to connect to")
	configureCmd.Flags().StringVar(&keyFlag, "key", "", "The api key")
	configureCmd.Flags().StringVar(&secretFlag, "secret", "", "The api secret")
	configureCmd.Flags().StringVar(&profileName, "profileName", "default", "The name of the auth to configure")
}
