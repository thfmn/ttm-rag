#!/usr/bin/env node
/**
 * Lightpanda MCP Server (Node ESM, stdio transport)
 *
 * Exposes tools:
 *  - lightpanda_fetch_dump(url, timeout?): HTML from `lightpanda fetch --dump`
 *  - lightpanda_fetch_text(url, timeout?): Plain text extracted from HTML
 *  - lightpanda_fetch_links(url, timeout?): Unique href list from anchors
 *
 * Configuration via environment:
 *  - LIGHTPANDA_BIN: absolute path to lightpanda binary (default: "lightpanda" on PATH)
 *  - LIGHTPANDA_USE_DOCKER: "true" to use Docker instead of local binary
 *  - LIGHTPANDA_DOCKER_IMAGE: Docker image tag (default: "lightpanda/browser:nightly")
 *  - LIGHTPANDA_DISABLE_TELEMETRY: "true" (default) to disable telemetry for subprocess
 *
 * IMPORTANT:
 *  - Requires @modelcontextprotocol/sdk as a dependency (install manually).
 *  - Does not install or start Lightpanda for you; follow docs/how-to/lightpanda_mcp_setup.md.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'node:child_process';
import { setTimeout as delay } from 'node:timers/promises';

const SERVER_NAME = 'lightpanda-mcp';
const SERVER_VERSION = '0.1.0';

// Environment & defaults
const BIN = process.env.LIGHTPANDA_BIN || 'lightpanda';
const USE_DOCKER = (process.env.LIGHTPANDA_USE_DOCKER || 'false').toLowerCase() === 'true';
const DOCKER_IMAGE = process.env.LIGHTPANDA_DOCKER_IMAGE || 'lightpanda/browser:nightly';
const DISABLE_TELEMETRY = (process.env.LIGHTPANDA_DISABLE_TELEMETRY || 'true').toLowerCase() === 'true';

function assertString(name, v) {
  if (typeof v !== 'string' || !v.trim()) {
    throw new McpError(ErrorCode.InvalidParams, `Invalid or missing "${name}" (expected non-empty string)`);
  }
}

function normalizeTimeout(ms) {
  const n = Number(ms);
  if (!Number.isFinite(n) || n <= 0) return 30000; // 30s default
  return Math.min(n, 180000); // clamp to 3m max
}

function runCommand(cmd, args, opts = {}) {
  const { cwd, env, timeoutMs = 30000 } = opts;
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      cwd,
      env: { ...process.env, ...env },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    let killed = false;

    const timer = setTimeout(() => {
      killed = true;
      child.kill('SIGKILL');
    }, timeoutMs);

    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    child.on('error', (err) => {
      clearTimeout(timer);
      reject(new McpError(ErrorCode.InternalError, `Failed to spawn "${cmd}": ${err.message}`));
    });

    child.on('close', (code) => {
      clearTimeout(timer);
      if (killed) {
        reject(new McpError(ErrorCode.InternalError, `Command timed out after ${timeoutMs} ms`));
      } else if (code !== 0) {
        reject(new McpError(ErrorCode.InternalError, `Command exited with code ${code}: ${stderr || stdout}`));
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

function parseHtmlFromDump(output) {
  // Lightpanda logs informational lines before HTML. Try to find first angle-bracket document start.
  const idxDoctype = output.indexOf('<!DOCTYPE');
  const idxHtml = output.indexOf('<html');
  let start = -1;
  if (idxDoctype !== -1) start = idxDoctype;
  else if (idxHtml !== -1) start = idxHtml;
  else {
    // fallback: first '<' that looks like a tag
    const m = output.match(/<[a-zA-Z!/?]/);
    start = m ? m.index : -1;
  }
  if (start !== -1) return output.slice(start);
  // If nothing matched, return whole output (best effort)
  return output;
}

function htmlToText(html) {
  try {
    // Remove scripts/styles
    let text = html.replace(/<script[\s\S]*?<\/script>/gi, '')
                   .replace(/<style[\s\S]*?<\/style>/gi, '');
    // Line breaks for block-ish tags
    text = text.replace(/<br\s*\/?>/gi, '\n')
               .replace(/<\/p>/gi, '\n')
               .replace(/<\/h[1-6]>/gi, '\n')
               .replace(/<\/li>/gi, '\n');
    // Strip tags
    text = text.replace(/<[^>]+>/g, ' ');
    // Decode basic entities
    const entities = {
      '&': '&',
      '<': '<',
      '>': '>',
      '"': '"',
      '&#39;': "'",
      '&nbsp;': ' ',
    };
    text = text.replace(/(&|<|>|"|&#39;|&nbsp;)/g, (m) => entities[m] || m);
    // Numeric entities
    text = text.replace(/&#(\d+);/g, (_, d) => {
      try { return String.fromCodePoint(parseInt(d, 10)); } catch { return _; }
    });
    // Collapse whitespace
    text = text.replace(/[ \t]+/g, ' ')
               .replace(/\s*\n\s*/g, '\n')
               .trim();
    return text;
  } catch {
    return html;
  }
}

function extractLinks(html) {
  const links = new Set();
  const re = /<a\b[^>]*\bhref\s*=\s*["']([^"'>]+)["'][^>]*>/gi;
  let m;
  while ((m = re.exec(html)) !== null) {
    const href = m[1].trim();
    if (href) links.add(href);
  }
  return Array.from(links);
}

async function lightpandaDump(url, timeoutMs) {
  const childEnv = {};
  if (DISABLE_TELEMETRY) {
    childEnv.LIGHTPANDA_DISABLE_TELEMETRY = 'true';
  }
  let cmd, args;
  if (USE_DOCKER) {
    cmd = 'docker';
    const envArgs = DISABLE_TELEMETRY ? ['-e', 'LIGHTPANDA_DISABLE_TELEMETRY=true'] : [];
    args = ['run', '--rm', ...envArgs, DOCKER_IMAGE, 'fetch', '--dump', url];
  } else {
    cmd = BIN;
    args = ['fetch', '--dump', url];
  }
  const { stdout } = await runCommand(cmd, args, { env: childEnv, timeoutMs });
  return parseHtmlFromDump(stdout);
}

class LightpandaMcpServer {
  constructor() {
    this.server = new Server(
      { name: SERVER_NAME, version: SERVER_VERSION },
      { capabilities: { resources: {}, tools: {} } },
    );

    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'lightpanda_fetch_dump',
          description: 'Fetch a URL with JS enabled using Lightpanda (returns HTML).',
          inputSchema: {
            type: 'object',
            properties: {
              url: { type: 'string', description: 'URL to fetch' },
              timeout: { type: 'number', description: 'Timeout in milliseconds (default 30000; max 180000)' },
            },
            required: ['url'],
          },
        },
        {
          name: 'lightpanda_fetch_text',
          description: 'Fetch a URL and return plain text extracted from HTML.',
          inputSchema: {
            type: 'object',
            properties: {
              url: { type: 'string', description: 'URL to fetch' },
              timeout: { type: 'number', description: 'Timeout in milliseconds (default 30000; max 180000)' },
            },
            required: ['url'],
          },
        },
        {
          name: 'lightpanda_fetch_links',
          description: 'Fetch a URL and return a JSON array of unique anchor hrefs.',
          inputSchema: {
            type: 'object',
            properties: {
              url: { type: 'string', description: 'URL to fetch' },
              timeout: { type: 'number', description: 'Timeout in milliseconds (default 30000; max 180000)' },
            },
            required: ['url'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const name = request.params.name;
      const args = request.params.arguments || {};
      assertString('url', args.url);
      const timeoutMs = normalizeTimeout(args.timeout);

      if (name === 'lightpanda_fetch_dump') {
        const html = await lightpandaDump(args.url, timeoutMs);
        return { content: [{ type: 'text', text: html }] };
      }
      if (name === 'lightpanda_fetch_text') {
        const html = await lightpandaDump(args.url, timeoutMs);
        const text = htmlToText(html);
        return { content: [{ type: 'text', text }] };
      }
      if (name === 'lightpanda_fetch_links') {
        const html = await lightpandaDump(args.url, timeoutMs);
        const links = extractLinks(html);
        return { content: [{ type: 'text', text: JSON.stringify(links, null, 2) }] };
      }
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    });

    this.server.onerror = (err) => {
      console.error(`[${SERVER_NAME}] Error:`, err?.stack || err?.message || String(err));
    };

    process.on('SIGINT', async () => {
      try { await this.server.close(); } catch {}
      process.exit(0);
    });
    process.on('SIGTERM', async () => {
      try { await this.server.close(); } catch {}
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error(`[${SERVER_NAME}] running on stdio (docker=${USE_DOCKER} image=${DOCKER_IMAGE} bin=${BIN})`);
  }
}

const srv = new LightpandaMcpServer();
srv.run().catch((e) => {
  console.error(`[${SERVER_NAME}] fatal`, e?.stack || e?.message || String(e));
  process.exit(1);
});
