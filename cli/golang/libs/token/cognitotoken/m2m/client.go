package m2m

import (
	"context"

	"github.com/aws/aws-sdk-go-v2/service/cognitoidentityprovider"
)

type Cognitoidentityprovider interface {
	DescribeUserPoolClient(ctx context.Context, params *cognitoidentityprovider.DescribeUserPoolClientInput, optFns ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.DescribeUserPoolClientOutput, error)
	ListUserPoolClients(context.Context, *cognitoidentityprovider.ListUserPoolClientsInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.ListUserPoolClientsOutput, error)
	AdminListGroupsForUser(context.Context, *cognitoidentityprovider.AdminListGroupsForUserInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.AdminListGroupsForUserOutput, error)
	GetGroup(context.Context, *cognitoidentityprovider.GetGroupInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.GetGroupOutput, error)
	ListUsersInGroup(context.Context, *cognitoidentityprovider.ListUsersInGroupInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.ListUsersInGroupOutput, error)
	CreateGroup(context.Context, *cognitoidentityprovider.CreateGroupInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.CreateGroupOutput, error)
	AdminCreateUser(context.Context, *cognitoidentityprovider.AdminCreateUserInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.AdminCreateUserOutput, error)
	AdminAddUserToGroup(context.Context, *cognitoidentityprovider.AdminAddUserToGroupInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.AdminAddUserToGroupOutput, error)
	AdminDeleteUser(context.Context, *cognitoidentityprovider.AdminDeleteUserInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.AdminDeleteUserOutput, error)
	AdminUpdateUserAttributes(context.Context, *cognitoidentityprovider.AdminUpdateUserAttributesInput, ...func(*cognitoidentityprovider.Options)) (*cognitoidentityprovider.AdminUpdateUserAttributesOutput, error)
}
