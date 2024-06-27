package auth

import (
	"encoding/json"
	"fmt"

	"github.com/pkg/errors"
	"github.com/spf13/cobra"

	//"fmt"

	"portal/libs/cmds"
)

var awsCommand = &cobra.Command{
	Use:   "aws",
	Short: "Returns credentials for the AWS CLI process",
	PreRunE: func(cmd *cobra.Command, args []string) error {
		return validateInputAWS(awsProject)
	},
	Long: `This command should not be used regularly by end users.
It can be called from your AWS credential process with
"sh -c 'portal auth aws -p cvr-pbac-iam-test-project-2-prd-demo"
`,
	RunE: func(cmd *cobra.Command, args []string) error {
		awscred, err := cmds.GetAWSRole(cmd.Context(), awsProject, awsEnvironment)
		if err != nil {
			return err
		}
		output, err := json.MarshalIndent(awscred, "", "    ")
		fmt.Println(string(output))
		if err != nil {
			return err
		}
		return err
	},
}

func validateInputAWS(awsProject string) error {
	if awsProject == "" {
		return errors.New("You should provide a project name")
	}
	return nil
}

var (
	awsProject string
	awsEnvironment string
)

func init() {
	Cmd.AddCommand(awsCommand)
	awsCommand.Flags().StringVarP(&awsProject, "project", "p", "", "The project to assume a role for")
	awsCommand.Flags().StringVarP(&awsEnvironment, "environment", "e", "", "The environment to assume a role in")
}
