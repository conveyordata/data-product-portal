# Data product Portal Package

This Python package should simplify the interaction with the Data Product Portal API when using Python.
The package supports Python 3.10 and above.

If you want to learn more about Data Product Portal, you can visit it's [website](https://portal.dataminded.com/).

## Authentication

The package currently only supports the device code flow for authentication.
To make authentication work, you need to set the following environment variables:

```bash
export PORTAL_AUTH_MODE="device" # Is the default authentication mode
export PORTAL_CLIENT_ID="" # The client id for the portal app integration in the cognito user pool
export PORTAL_CLIENT_SECRET="" # The client secret for the portal app integration in the cognito user pool
export PORTAL_TOKEN_URL="https://<cognito-domain>.amazoncognito.com/oauth2/token" # This is the token URL of the Cognito user pool.
# Take a look at .well-known/openid-configuration of your cognito domain for more details
export PORTAL_BASE_URL="https://<portal-domain>/api/"
```

## Changelog

### Unreleased

- Initial version of authentication
- Support pushing data quality summaries
