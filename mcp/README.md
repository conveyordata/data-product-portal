# Local development of MCP server

When testing the MCP server locally, keep in mind the following:

- You need to have OIDC authentication set up and running
- Start the backend locally instead of in Docker as that does not work
- Use the correct endpoint, normally this should be `http://localhost:5050`

## Useful curl commands

The following commands you can use to test the basic info of your MCP server and it's tools description. It does not need authentication.
This is also what claude/cursor do when you connect the MCP server.

```bash
SESSION_ID=$(curl -sS -X POST http://portal-dev.demo1.conveyordata.com/mcp/mcp \                                                                                                                     ─╯
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -D /dev/stderr \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  2>&1 >/dev/null | grep -i mcp-session-id | awk '{print $2}' | tr -d '\r')

echo "Session ID: $SESSION_ID"

curl -X POST http://localhost:5050/mcp/mcp \                                                                                                                                                         ─╯
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

## Alternative Oauth setup for MCP

Niels had issues with the Oauth support in the MCP server.
For now we kept the existing system as the assumption is that it works for most users.
Documenting here an alternative setup that worked for Niels:

### Use the dpp-sdk to get an access token

First step is to rewrite the remote-proxy to use the dpp-sdk to get an access token.
```python
from __future__ import annotations

import os

from fastmcp import Client, FastMCP
from fastmcp.client import BearerAuth
from fastmcp.client.auth.oauth import OAuth
from fastmcp.utilities.logging import get_logger
from key_value.aio.stores.memory import MemoryStore
from sdk.auth import PortalAuth
logger = get_logger(__name__)

endpoint = os.getenv("ENDPOINT", "http://localhost:5050")
os.environ["PORTAL_BASE_URL"] = "http://localhost:5050/api"
os.environ["PORTAL_CLIENT_ID"] = "<>"
os.environ["PORTAL_CLIENT_SECRET"] = "<>"

auth = PortalAuth()
token = auth.get_access_token()
client = Client(f"{endpoint}/mcp/mcp", auth=BearerAuth(token=token))

server = FastMCP.as_proxy(client, name="AuthenticatedProxyDataProductPortal")

if __name__ == "__main__":
    server.run()
```

In order to get this to work we need to also install the dpp-sdk when configuring the MCP. MCP config:
```
{
  "mcpServers": {
    "dataProductPortal": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "--with",
        "attrs",
        "--with",
        "<python wheel/pypi package for dpp-sdk>",
        "fastmcp",
        "run",
        "<path>/remote_proxy.py"
      ],
      "env": {
        "ENDPOINT": "http://localhost:5050"
      }
    }
  }
}
```
Note: if we want to give this to customers, we need to publish the dpp-sdk to pypi instead of using a local wheel.
