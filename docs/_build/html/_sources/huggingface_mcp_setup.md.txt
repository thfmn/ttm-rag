# Hugging Face MCP Server integration with Cline

This guide documents how we added the official Hugging Face MCP server to Cline and how you can verify and use it.

References:
- Hugging Face MCP Server repo: https://github.com/evalstate/hf-mcp-server
- Hugging Face MCP endpoint: https://huggingface.co/mcp (login flow at https://huggingface.co/mcp?login)
- Cline docs:
  - Configuring MCP Servers: https://docs.cline.bot/mcp/configuring-mcp-servers
  - Adding MCP Servers from GitHub: https://docs.cline.bot/mcp/adding-mcp-servers-from-github
  - Connecting to a Remote Server: https://docs.cline.bot/mcp/connecting-to-a-remote-server

## What we implemented

We added a remote MCP server entry for Hugging Face using HTTP transport (Streamable HTTP JSON mode provided by HF). Authentication is provided via an Authorization header with your Hugging Face access token.

Settings file location (VS Code global):
- Linux: ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

A backup was saved as:
- ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json.bak

## Security note

- Your Hugging Face token is stored in plain text in the VS Code global settings file above. Rotate it if needed and treat that file as sensitive.
- Alternative: do not store a token in the file and use the login flow at https://huggingface.co/mcp?login.

## Final configuration snippet

This entry was added to the mcpServers object:

```json
"huggingface": {
  "url": "https://huggingface.co/mcp",
  "headers": {
    "Authorization": "Bearer <YOUR_HF_TOKEN>"
  },
  "disabled": false,
  "timeout": 60,
  "autoApprove": []
}
```

In our environment, we used the provided token and applied it to the Authorization header.

## Verification steps in Cline

1. Open Cline in VS Code.
2. Click the menu (⋮) in the Cline panel and select “MCP Servers”.
3. Go to the “Installed” tab.
4. Locate the server named “huggingface”.
5. If the status indicator is not green, click “Restart Server”.
6. If the server doesn’t appear, click “Advanced MCP Settings” and verify the JSON, or reload the VS Code window.

Expected behavior:
- The server should connect over HTTP to https://huggingface.co/mcp using your token.
- Tools/resources from Hugging Face should be listed in the server panel once connected.

## Quick test ideas

From a Cline conversation:
- “List the available tools on the ‘huggingface’ MCP server.”
- “Use the huggingface MCP server to search Hugging Face docs for ‘transformers pipeline’.”
- “List some popular Hugging Face Spaces.”

Notes from the HF repo:
- Tools commonly exposed include search and fetch capabilities for HF docs/content (e.g., hf_doc_search, hf_doc_fetch) and an Authenticate tool if enabled.
- The server supports multiple transports; we’re using the remote HTTP endpoint.

## Troubleshooting

- 401/403 errors: Verify the Authorization header and token scope (re-issue a token at https://huggingface.co/settings/tokens).
- Connection issues: Ensure network access to huggingface.co, no intercepting proxies, and the URL is exactly https://huggingface.co/mcp.
- Timeouts: Increase the “timeout” setting on the server entry in cline_mcp_settings.json.
- Not seeing tools: Confirm the server is “Enabled” in the MCP Servers UI and restart it. If still not visible, reload VS Code.
- Prefer login flow: Remove the Authorization header and visit https://huggingface.co/mcp?login for OAuth-style login.

## Optional: Local STDIO alternative

Instead of the remote HTTP endpoint, you can run a local STDIO server with npx:
```
npx @llmindset/hf-mcp-server
```

And configure Cline with:
```json
"huggingface-stdio": {
  "command": "npx",
  "args": ["-y", "@llmindset/hf-mcp-server"],
  "env": {
    "HF_TOKEN": "<YOUR_HF_TOKEN>"
  },
  "disabled": false,
  "timeout": 60,
  "type": "stdio"
}
```

This keeps your token local and avoids network transport configuration, at the cost of needing to run the process locally.

## Uninstall / removal

- Open the MCP settings file: ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
- Remove the “huggingface” entry from mcpServers.
- Save the file and restart Cline.
- Optionally delete the backup file (.bak) after confirming everything works.

## Change log for this project

- Created backup of MCP settings JSON.
- Added remote “huggingface” MCP server entry with Authorization header.
- Documented verification and testing procedures in this guide.
