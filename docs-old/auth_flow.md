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
