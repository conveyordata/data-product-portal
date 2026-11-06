---
sidebar_position: 1
title: Authentication
description: Authentication flows explained
---

# Authentication

You can find diagrams explaining the different authentication flows used in the Data Product Portal below.
This is useful background information if you would like to implement wrappers around Data Product Portal functionality.

## Basic Authentication (OIDC)

``` mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Cognito
    participant Backend
    alt user initiates auth
      User->>Frontend: Initiates Auth Flow
    else user makes call
     User->>Frontend:  Requests Resource
     Frontend->>Backend: Makes unauthenticated HTTPS request
     Backend->>Frontend: Responds with 401 Unauthenticated
    end

    Frontend->>Cognito: Redirects to Cognito with Auth Request
    Cognito->>User: Presents Authentication UI
    User->>Cognito: Submits Credentials
    Cognito->>Frontend: Redirects with ID Token & Access Token
    Frontend->>User: Shows Authenticated Session
    User->>Frontend: Requests Resource
    Frontend->>Backend: API Call with Access Token
    Backend->>Cognito: Validates Access Token
    Cognito->>Backend: Token Valid
    Backend->>Frontend: Responds with Resource
```

---

## Device Flow
The device flow is used to authenticate from machines without browser access or decent user interfaces to portal by redirecting the authentication request to your browser.

``` mermaid
sequenceDiagram
    participant User
    participant Headless Device
    participant Cognito
    participant Backend

    Note over Headless Device, Backend: Device requests code from Backend

    Headless Device->>Backend: Request device code
    Backend->>Headless Device: Provide user_code, device_code, verification_uri

    Note over User, Headless Device: User authorizes device using another device (e.g., smartphone or browser)

    User->>Cognito: Navigate to verification_uri and confirm user_code
    Cognito->>User: Prompt for Cognito login credentials
    User->>Cognito: Provide credentials
    Cognito->>Backend: Store authorization code in backend
    Cognito->>User: Confirm authorization

    Note over Headless Device, Backend: Device polls backend for the authorization token (can start immediately after device_code request)

    loop until token received or timeout
        Headless Device->>Backend: Poll with device_code for authorization token
    alt authorization token received
Backend->>Cognito: token call to fetch access token
Cognito->>Backend: return access token
    else
    end
        Backend->>Headless Device: Respond with pending, access token (success), or error
    end

    Note over Headless Device, Backend: Device uses access token to access Backend

    Headless Device->>Backend: Access with access token
    Backend->>Headless Device: Grant access
```

---

## Setting up OIDC

Portal has been tested with AWS Cognito but should work with any OIDC provider.

OIDC returns identity, refresh and access tokens.
Providers may vary in the information they pass in tokens, and the application depends on this information, so integrating a new provider might require some code changes there as well.

The claims our provider is required to pass are at least email and name; family_name is used as the last name when present. The given_name claim is used as the first name; if it is missing, name is used instead.

The backend reads the current user from one of two sources, set with `OIDC_IDENTITY_SOURCE`:

| Setting | Default | Meaning |
|---|---|---|
| `OIDC_IDENTITY_SOURCE` | `userinfo` | `userinfo` asks the provider's userinfo endpoint with the access token. `access_token` reads the claims of the validated access token and never calls userinfo. |
| `OIDC_USER_ID_CLAIM` | `sub` | The access token claim that identifies a user. It is stored as the user's external id, so don't change it once users have logged in. |
| `OIDC_EMAIL_CLAIM` | `email` | The access token claim that holds the email address. Only used with `access_token`. |

Use `userinfo` for Cognito, whose access tokens carry no email. Keycloak works with both. With `userinfo`, a rejected access token or an answer without a valid email is a 401, and an unreachable or failing endpoint is a 503.

Use `access_token` for providers whose userinfo endpoint does not accept the portal's access token, such as Microsoft Entra ID. When given_name is missing, name is split into first and last name: on the comma for names written as "Last, First", otherwise on the last space. An identity read from the access token links to an existing user with the same email only when the token's `email` claim holds that address and `email_verified` is true; otherwise a login whose email already belongs to another user is rejected. For Entra ID, use:

```
OIDC_IDENTITY_SOURCE=access_token
OIDC_USER_ID_CLAIM=oid
OIDC_EMAIL_CLAIM=preferred_username
```

Entra ID's `sub` differs per application, while `oid` is the same for a user across the tenant. With the Helm chart, set these settings through `extraConfigMapValues`.

### Cognito setup

This is not a full explanation on how to set up Cognito, but the key points to keep in mind for the Portal are listed below:

- Add email, family_name and name to the required_attributesin your user pool.
- Create an app integration and note the client ID and secret.
- Find the authority URL using the format: `https://cognito-idp.<COGNITO_REGION>.amazonaws.com/<COGNITO_USER_POOL_ID>`

### Configuring callback urls

We also need to configure the right callback urls for the app integration.

For a production setup the following is required:
```
https://<HOST>/
https://<HOST>/api/auth/device/callback/
https://<HOST>/logout/
https://<HOST>/mcp/auth/callback #Needed for the MCP server authentication flow
```

For development the following extra callbacks are required:
```
http://localhost:3000/
http://localhost:3000/logout/
http://localhost:5050/
http://localhost:5050/logout/
http://localhost:5050/api/auth/device/callback/
https://localhost:5050/mcp/auth/callback #Needed for the MCP server authentication flow
```

The following blog post goes a bit more into details: [Data Product Portal Integrations 1: OIDC](https://medium.com/conveyordata/data-product-portal-integrations-1-oidc-8d1dcdc0896e)

To understand better the details of the Device code Flow, take a look at the following [blogpost](https://medium.com/datamindedbe/demystifying-device-flow-ae15854bac24) instead.
