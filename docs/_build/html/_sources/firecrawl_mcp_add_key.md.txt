How to add FIRECRAWL_API_KEY to cline_mcp_settings.json
------------------------------------------------------

Target file (already updated with the server entry):
/var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

Goal
- Add an env block for the `github.com/mendableai/firecrawl-mcp-server` entry so the MCP system can start the Firecrawl MCP with your API key.

Option A — Manual edit (recommended if you prefer GUI or editor)
1. Open the settings file in your editor:
   - Visual Studio Code:
     code "/var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
   - Nano:
     nano "/var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"

2. Locate the server entry for `github.com/mendableai/firecrawl-mcp-server` and insert an `env` object. The final server block should look like this (replace fc-YOUR_API_KEY with your key):

```json
"github.com/mendableai/firecrawl-mcp-server": {
  "command": "npx",
  "args": [
    "-y",
    "firecrawl-mcp"
  ],
  "env": {
    "FIRECRAWL_API_KEY": "fc-YOUR_API_KEY"
  },
  "disabled": false,
  "autoApprove": []
}
```

3. Save the file. The system that watches MCP settings may auto-start the server; otherwise start the server manually (see commands below).

Option B — Programmatic edit using jq (safe for scripting)
- Install jq if you don't have it (example for Debian/Ubuntu; run locally yourself):
  sudo apt-get update && sudo apt-get install -y jq

- Replace the placeholder key in a single command (do not run this on the assistant; run locally):

```bash
jq --arg key 'fc-YOUR_API_KEY' \
'.mcpServers["github.com/mendableai/firecrawl-mcp-server"].env = {"FIRECRAWL_API_KEY": $key}' \
/var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json \
> /tmp/cline_mcp_settings.json && mv /tmp/cline_mcp_settings.json /var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

- Verify:
  jq . /var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

Quick alternative (do not store key in file)
- If you prefer not to store the API key in the JSON, you can run the MCP server manually with the env var at runtime:

```bash
# Quick run with npx (recommended for testing)
FIRECRAWL_API_KEY="fc-YOUR_API_KEY" npx -y firecrawl-mcp

# SSE local mode (expose http://localhost:3000/sse)
SSE_LOCAL=true FIRECRAWL_API_KEY="fc-YOUR_API_KEY" npx -y firecrawl-mcp
```

Notes and security
- Do not commit your API key to any public repo.
- Storing secrets in local config files is convenient but may be less secure than using your OS secrets manager. Use whichever approach fits your security needs.
- If you add the env key to the cline_mcp_settings.json, the MCP manager (VSCode/global integration) may auto-start the server and expose its tools. If it does not auto-start, manually start the server as shown above.

What to do next
- Run one of the commands above locally (either the jq edit + wait for auto-start, or run the server manually with the FIRECRAWL_API_KEY env). After you confirm the MCP server is running and connected, tell me and I will demonstrate a tool call (for example `firecrawl_search` or `firecrawl_scrape`) from the assistant.

Example demonstration command (what I'll run once the server is visible)
- After you confirm the server is running, I'll issue:

use_mcp_tool
server_name: "github.com/mendableai/firecrawl-mcp-server"
tool_name: "firecrawl_search"
arguments:
{
  "query": "latest AI research 2023",
  "limit": 3,
  "lang": "en",
  "scrapeOptions": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}

Task progress
- [x] Load MCP documentation
- [x] Read existing cline_mcp_settings.json
- [x] Create MCP server directory (/var/home/akr/Documents/Cline/MCP/github.com/mendableai/firecrawl-mcp-server)
- [x] Add server entry to cline_mcp_settings.json with name "github.com/mendableai/firecrawl-mcp-server" (disabled=false, autoApprove=[])
- [ ] Clone the firecrawl-mcp-server repository into the new directory
- [ ] Inspect repository to determine build/run steps
- [x] Provide user-run commands to install dependencies and run the server (npx/npm)
- [x] Show how to add FIRECRAWL_API_KEY to cline_mcp_settings.json
- [ ] Demonstrate server capability by calling one tool (requires server running)
