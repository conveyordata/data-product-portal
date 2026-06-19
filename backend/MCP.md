# MCP Server development

You can use the MCP server locally in 2 modes: With Ouath enabled and without.

To test with oauth enabled you have to provide the following in your `.env` file:

```dotenv
OIDC_CLIENT_ID=<>
OIDC_CLIENT_SECRET=<>
OIDC_AUTHORITY=<>
OIDC_REDIRECT_URI=http://localhost:5050/
OIDC_ENABLED=true


MCP_AUTH_REDIRECT_URIS='["http://127.0.0.1:*","https://vscode.dev/redirect", "http://127.0.0.1:*/callback", "cursor://anysphere.cursor-mcp/oauth/callback"]'```

The `MCP_AUTH_REDIRECT_URIS` are currently setup for VSCode integration, cursor, github copilot,
for other tools you have to figure out their redirect paths. This is easy try to connect and you will get an error screen.

## Setting it up for VSCode

Use the command `MCP: Open User Configuration`, this will open the mcp.json, configure it like this:
```
{
	"servers": {
		"Portal": {
			"url": "http://localhost:5050/mcp/",
			"type": "http"
		}
	},
	"inputs": []
}
```

When oauth is enabled, you will be redirected to the OIDC provider for authentication.
After successful authentication, you will be redirected back to the MCP server.

Above the MCP server in the `mcp.json` there is a state, and there are buttons (restart, stop). Clicking on the more
button allows you to click `show Output`, to see the logs of this MCP server connection.

Under more you can also disconnect account, to retry the login flow.
