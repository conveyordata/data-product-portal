---
sidebar_position: 1
title: Authentication
description: Authentication flows explained
---

# Authentication

The Data Product Portal signs users in with OpenID Connect (OIDC). It has been tested with AWS Cognito and should work with any OIDC provider. The settings below cover Keycloak and Microsoft Entra ID as well.
The diagrams below show the sign-in flows. They are useful background if you build a wrapper around the portal.

## Browser sign-in

The backend fetches the provider's public keys once at startup, and uses them to check every access token itself.
It only asks for the user's details when it sees a user for the first time.

``` mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Provider as Identity provider
    participant Backend

    User->>Frontend: Opens the portal
    Frontend->>Provider: Redirects to sign in
    User->>Provider: Signs in
    Provider->>Frontend: Redirects back with ID token and access token
    Frontend->>Backend: API call with access token
    Backend->>Backend: Checks signature, issuer, audience and expiry
    opt First request of an unknown user
        alt OIDC_IDENTITY_SOURCE=userinfo
            Backend->>Provider: Userinfo request with access token
            Provider->>Backend: Email and names
        else OIDC_IDENTITY_SOURCE=access_token
            Backend->>Backend: Reads email and names from the access token
        end
        Backend->>Backend: Creates or updates the user
    end
    Backend->>Frontend: Responds with resource
```

---

## Device flow

The device flow signs in machines without a browser, such as the CLI. You confirm the sign-in in a browser on another device.

``` mermaid
sequenceDiagram
    participant User
    participant Device as Headless device
    participant Backend
    participant Provider as Identity provider

    Device->>Backend: Requests a device code
    Backend->>Device: user_code, device_code and verification_uri

    User->>Backend: Opens verification_uri and confirms user_code
    Backend->>User: Redirects to the provider
    User->>Provider: Signs in
    Provider->>Backend: Redirects back with an authorization code
    Backend->>User: Confirms the device is authorized

    loop Until token, error or timeout
        Device->>Backend: Polls with device_code
        opt Authorization code received
            Backend->>Provider: Exchanges the code for tokens
            Provider->>Backend: Access token
        end
        Backend->>Device: Pending, access token or error
    end

    Device->>Backend: API call with access token
```

---

## Setting up OIDC

### Where the backend reads the user from

The backend needs to know who is calling: a stable user id, an email and a name.
It reads them from one of two sources, set with `OIDC_IDENTITY_SOURCE`.

| Setting | Default | Meaning |
|---|---|---|
| `OIDC_IDENTITY_SOURCE` | `userinfo` | `userinfo` asks the provider's userinfo endpoint, using the access token. `access_token` reads the claims of the access token itself and never calls userinfo. |
| `OIDC_USER_ID_CLAIM` | `sub` | The access token claim that identifies a user. |
| `OIDC_EMAIL_CLAIM` | `email` | The access token claim that holds the email address. Only used with `access_token`. |

:::warning
The user id claim is stored as the user's external id, so don't change it once users have signed in.
Pick an id the provider sets and users can't change, such as `sub` or Entra ID's `oid`.
Never pick `email` or `preferred_username`: whoever can change that value can take over the account.
:::

Which source to pick:

| Provider | Source | Why |
|---|---|---|
| AWS Cognito | `userinfo` | Its access tokens carry no email. |
| Keycloak | either | It puts email and names in both. |
| Microsoft Entra ID | `access_token` | Its userinfo endpoint doesn't accept the portal's access token. |

### Required claims

With `userinfo`, the answer must hold `email` and `name`.
`given_name` is used as the first name, with `name` as fallback, and `family_name` as the last name.
A rejected access token or an answer without a valid email gives a 401. An unreachable or failing endpoint gives a 503.

With `access_token`, only the claim named by `OIDC_EMAIL_CLAIM` is required.
Names come from `given_name` and `family_name`.
Without `given_name`, `name` is split into first and last name: on the comma for "Last, First", otherwise on the last space.
Without any name, the part of the email before the @ becomes the first name.

### Linking to an existing user

A user who signs in for the first time can already exist in the portal with the same email, for example because they were created before their first sign-in.
With `access_token`, the backend links the two only when the token's `email` claim holds that address and `email_verified` is true.
Otherwise the sign-in is rejected, so nobody can claim an account just by putting its email in a token.

### Microsoft Entra ID

```
OIDC_IDENTITY_SOURCE=access_token
OIDC_USER_ID_CLAIM=oid
OIDC_EMAIL_CLAIM=preferred_username
```

- Use `oid`, not `sub`: Entra ID's `sub` is different for every application, while `oid` is the same for a user across the tenant.
- Set `OIDC_AUDIENCE` to the audience of the portal's access token.
- The frontend requests only `openid profile email` today. With those scopes Entra ID issues an access token for Microsoft Graph, not for the portal. Requesting the portal's own API scope needs a frontend change that isn't available yet.
- Entra ID never sends `email_verified`, so a new sign-in never links to an existing user by email.

With the Helm chart, set these settings through `extraConfigMapValues`.

### Cognito setup

This is not a full explanation on how to set up Cognito, but the key points to keep in mind for the Portal are listed below:

- Add email, family_name and name to the required attributes in your user pool.
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
