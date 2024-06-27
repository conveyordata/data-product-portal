package m2m

import (
	"context"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/cognitoidentityprovider"
	"github.com/pkg/errors"
)

func GetM2MTokenClientIdClientSecret(
	ctx context.Context,
	cognitoClient Cognitoidentityprovider,
	userPoolId string,
	m2mName string,
) (string, string, error) {
	var clientId string
	paginator := cognitoidentityprovider.NewListUserPoolClientsPaginator(cognitoClient, &cognitoidentityprovider.ListUserPoolClientsInput{
		UserPoolId: aws.String(userPoolId),
	})
Exit:
	for paginator.HasMorePages() {
		output, err := paginator.NextPage(ctx)
		if err != nil {
			return "", "", fmt.Errorf("could not list user pool clients: %w", err)
		}
		for _, client := range output.UserPoolClients {
			if *client.ClientName == m2mName {
				clientId = *client.ClientId
				break Exit
			}
		}
	}
	if clientId == "" {
		return "", "", errors.New("could not find the m2m tokens")
	}
	output, err := cognitoClient.DescribeUserPoolClient(ctx, &cognitoidentityprovider.DescribeUserPoolClientInput{
		ClientId:   aws.String(clientId),
		UserPoolId: aws.String(userPoolId),
	})
	if err != nil {
		return "", "", fmt.Errorf("could not describe user pool for clientId: %w", err)
	}
	return *output.UserPoolClient.ClientId, *output.UserPoolClient.ClientSecret, nil
}
