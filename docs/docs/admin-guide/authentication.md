---
sidebar_position: 3
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

## Extra material

To find out more about how to integrate the Data Product Portal with OIDC, visit [this blogpost](https://medium.com/conveyordata/data-product-portal-integrations-1-oidc-8d1dcdc0896e)

To find out more about the details of the Device Flow, visit [this blogpost](https://medium.com/datamindedbe/demystifying-device-flow-ae15854bac24) instead.
