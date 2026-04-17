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
