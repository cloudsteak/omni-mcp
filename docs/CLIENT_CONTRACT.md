# Phase 2 Client Contract (`omni-studio`)

Target repo:
`/Users/sipp/dev/github.com/cloudsteak/omni-studio`

## Responsibilities

Client will:
- authenticate end users and external channels
- optionally receive Slack events/webhooks
- map user requests to MCP tool/resource/prompt calls
- forward validated calls to `omni-mcp`

Server (`omni-mcp`) will:
- execute MCP capabilities
- enforce server-side policy constraints
- return deterministic results and errors

## Recommended flow

1. User request enters client (UI or Slack)
2. Client authenticates + authorizes request
3. Client calls `omni-mcp` via MCP transport
4. Server executes tool/resource/prompt
5. Client formats and returns response to user/Slack
