import os

from fastmcp import Client, FastMCP

from app.core.auth.device_flows.device_flow_client import DeviceFlowClient

BASE_URL = "http://localhost:5050"  # Adjust to your API base URL
CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
AUTH_CLIENT_ID = os.getenv("OIDC_CLIENT_SECRET")

token_response = None
# Create client
if CLIENT_ID and AUTH_CLIENT_ID:
    client = DeviceFlowClient(
        base_url=BASE_URL,
        client_id=CLIENT_ID,
        auth_client_id=AUTH_CLIENT_ID,
    )

    # Perform authentication
    token_response = client.authenticate(scope="openid profile")

auth = None
if token_response:
    auth = token_response["access_token"]
client = Client("http://localhost:5050/mcp/mcp", auth=auth)

# Create proxy using the authenticated client
server = FastMCP.as_proxy(client, name="AuthenticatedProxyDataProductPortal")

if __name__ == "__main__":
    server.run()
