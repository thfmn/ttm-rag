# Lightpanda Browser MCP integration for Cline (VS Code)

This guide adds Lightpanda (a fast, headless browser with JS execution and CDP) to your Cline workflow via a local MCP server. You’ll be able to:
- Fetch dynamic pages with JS (`lightpanda_fetch_dump`, `lightpanda_fetch_text`)
- Extract links quickly (`lightpanda_fetch_links`)
- Choose runtime: local Lightpanda binary or Docker (no persistent container required)
- Keep telemetry disabled by default

The MCP server is implemented in this repo at:
- tools/lightpanda-mcp/index.js (Node, stdio transport)
- tools/lightpanda-mcp/package.json

Important project rules respected:
- No automatic installs or global changes
- Provide clear manual commands
- Document config and verification steps


## 1) Requirements

- Node.js 18+ (for running the MCP server script)
- EITHER:
  - Lightpanda binary available on your PATH (or specify LIGHTPANDA_BIN), OR
  - Docker installed (the MCP server can call `docker run` per request)
- Cline in VS Code (MCP-enabled)


## 2) Install dependencies (manual)

Install the MCP SDK dependency for the server:

```
cd /var/home/akr/dev/thai-traditional-medicine-rag-bot/tools/lightpanda-mcp
npm install
```

This installs:
- @modelcontextprotocol/sdk


## 3) Install Lightpanda runtime (choose one)

A) Local binary (Linux example)

```
# Download nightly binary (Linux x86_64)
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux

# Make executable and move to a directory on PATH (example)
chmod a+x ./lightpanda
mkdir -p /var/home/akr/bin
mv ./lightpanda /var/home/akr/bin/lightpanda

# Optionally add /var/home/akr/bin to PATH in your shell profile
# export PATH="/var/home/akr/bin:$PATH"
```

B) Docker (no local binary)

You don’t need to run a daemonized container. The MCP server will invoke `docker run --rm lightpanda/browser:nightly fetch --dump <url>` on demand.


## 4) Telemetry

Lightpanda collects telemetry by default. The MCP server sets `LIGHTPANDA_DISABLE_TELEMETRY=true` by default for all subprocesses. You can override via env if needed.


## 5) Add MCP server entry (Cline settings)

Edit your Cline MCP settings (VS Code global):
- /var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

Add a new entry under `mcpServers`:

Option 1: Use local Lightpanda binary
```json
"lightpanda-mcp": {
  "command": "node",
  "args": [
    "/var/home/akr/dev/thai-traditional-medicine-rag-bot/tools/lightpanda-mcp/index.js"
  ],
  "env": {
    "LIGHTPANDA_DISABLE_TELEMETRY": "true",
    "LIGHTPANDA_BIN": "/var/home/akr/bin/lightpanda"
  },
  "type": "stdio",
  "timeout": 120,
  "disabled": false,
  "autoApprove": []
}
```

Option 2: Use Docker
```json
"lightpanda-mcp": {
  "command": "node",
  "args": [
    "/var/home/akr/dev/thai-traditional-medicine-rag-bot/tools/lightpanda-mcp/index.js"
  ],
  "env": {
    "LIGHTPANDA_DISABLE_TELEMETRY": "true",
    "LIGHTPANDA_USE_DOCKER": "true",
    "LIGHTPANDA_DOCKER_IMAGE": "lightpanda/browser:nightly"
  },
  "type": "stdio",
  "timeout": 120,
  "disabled": false,
  "autoApprove": []
}
```

Notes:
- Keep `disabled=false` and `autoApprove=[]` (per Cline’s MCP defaults).
- Ensure Node 18+ is available on PATH for VS Code/Cline.


## 6) What tools are exposed

- lightpanda_fetch_dump
  - Input: { "url": string, "timeout"?: number(ms) }
  - Output: HTML as text (with Lightpanda info lines removed when possible)
- lightpanda_fetch_text
  - Input: { "url": string, "timeout"?: number(ms) }
  - Output: Plain text extracted from HTML
- lightpanda_fetch_links
  - Input: { "url": string, "timeout"?: number(ms) }
  - Output: JSON array of unique anchor hrefs

Timeout default = 30000ms, max = 180000ms


## 7) Verify in Cline

- In VS Code, open Cline panel → menu (⋮) → MCP Servers
- Find server: lightpanda-mcp
- If not connected, click “Restart Server”. If still not visible, click “Advanced MCP Settings” and verify the JSON, then reload the window.

Quick test from a Cline conversation:

Example 1: Fetch text
```
use_mcp_tool
server_name: "lightpanda-mcp"
tool_name: "lightpanda_fetch_text"
arguments:
{
  "url": "https://example.com",
  "timeout": 20000
}
```

Example 2: Fetch links
```
use_mcp_tool
server_name: "lightpanda-mcp"
tool_name: "lightpanda_fetch_links"
arguments:
{
  "url": "https://wikipedia.org"
}
```

Example 3: Full HTML
```
use_mcp_tool
server_name: "lightpanda-mcp"
tool_name: "lightpanda_fetch_dump"
arguments:
{
  "url": "https://lightpanda.io"
}
```


## 8) Optional: Agentic use via CDP (Puppeteer)

If you want full agentic control (click, form, evaluate JS), run Lightpanda’s CDP server and connect with Puppeteer:

Start Lightpanda CDP:
```
# Local binary
lightpanda serve --host 127.0.0.1 --port 9222
```

Puppeteer (Node) connect example:
```js
import puppeteer from "puppeteer-core";

const browser = await puppeteer.connect({
  browserWSEndpoint: "ws://127.0.0.1:9222"
});

const context = await browser.createBrowserContext();
const page = await context.newPage();

await page.goto("https://wikipedia.com/");
const links = await page.evaluate(() => Array.from(document.querySelectorAll("a")).map(a => a.href));
console.log(links);

await page.close();
await context.close();
await browser.disconnect();
```

Note:
- Playwright generally works but may select different code paths as Web API coverage changes (see Lightpanda README disclaimer).


## 9) Troubleshooting

- Node not found: Install Node.js 18+ and ensure `node` is on PATH for VS Code.
- Docker errors: Make sure you can run `docker run hello-world`. On Linux, ensure your user is in the `docker` group.
- Binary not found: Set `LIGHTPANDA_BIN` to the absolute path of `lightpanda` or use the Docker option.
- Timeouts: Increase `arguments.timeout` as needed; some dynamic sites may take longer to settle.
- HTML includes log lines: The server tries to strip prolog logs. If parsing fails, it returns raw output (best effort).
- Telemetry: Default disabled via env. Remove env if you wish to enable per Lightpanda’s policy.


## 10) Uninstall / removal

- Remove the `lightpanda-mcp` server entry from:
  /var/home/akr/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
- Optionally remove tools/lightpanda-mcp directory


## 11) Change log (for this integration)

- Added tools/lightpanda-mcp/index.js and package.json (local MCP server)
- Documented setup with binary and Docker runtime options
- Provided MCP settings JSON snippets and verification steps
