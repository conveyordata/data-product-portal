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
