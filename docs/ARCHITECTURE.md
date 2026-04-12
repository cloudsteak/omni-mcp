# Architecture

## Current state

`omni-mcp` is a modular Python MCP server using FastMCP:

- `src/omni_mcp/main.py`: CLI entrypoint and transport selection
- `src/omni_mcp/server.py`: server assembly and logging
- `src/omni_mcp/config.py`: validated environment config
- `src/omni_mcp/security.py`: shared security policy helpers
- `src/omni_mcp/skills/builtin.py`: built-in MCP tools/resources/prompts

## Phase mapping

1. Phase 1 (implemented): local MCP server
2. Phase 2 (planned in another repo): dedicated client in `omni-studio`, with optional Slack ingress
3. Phase 3 (implemented): Docker image and runtime defaults
4. Phase 4 (implemented baseline): Kubernetes-compatible Helm chart

## Runtime flow (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
flowchart LR
    U[User] --> C["omni-studio client<br/>(Phase 2)"]
    S[Slack] --> C
    C -->|MCP stdio / streamable-http| M[omni-mcp server]

    M --> P["SecurityPolicy<br/>(HTTPS, allowlist, limits)"]
    M --> K["Built-in Skills<br/>Tools / Resources / Prompts"]
    K --> R[Result]
    R --> C
    C --> U

    classDef actor fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef client fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;
    classDef server fill:#FFF3E0,stroke:#FB8C00,color:#E65100,stroke-width:1px;
    classDef policy fill:#F3E5F5,stroke:#8E24AA,color:#4A148C,stroke-width:1px;
    classDef result fill:#FBE9E7,stroke:#F4511E,color:#BF360C,stroke-width:1px;

    class U,S actor;
    class C client;
    class M,K server;
    class P policy;
    class R result;
```

## Component structure (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
graph TD
    A["src/omni_mcp/main.py<br/>CLI + transport"] --> B["src/omni_mcp/server.py<br/>FastMCP assembly"]
    B --> C["src/omni_mcp/config.py<br/>Settings"]
    B --> D["src/omni_mcp/security.py<br/>Policy"]
    B --> E["src/omni_mcp/skills/builtin.py<br/>Tools/Resources/Prompts"]

    F["Dockerfile<br/>container runtime"] --> B
    G["deploy/helm/omni-mcp<br/>Kubernetes packaging"] --> F

    classDef app fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef core fill:#FFF3E0,stroke:#FB8C00,color:#E65100,stroke-width:1px;
    classDef deploy fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;

    class A,C,D,E app;
    class B core;
    class F,G deploy;
```

## Deployment topology (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
flowchart TD
    subgraph Local[Local development]
        L1[Developer machine]
        L2[omni-mcp --transport stdio]
        L1 --> L2
    end

    subgraph Docker[Container runtime]
        D1[Docker host]
        D2[omni-mcp container :8080]
        D1 --> D2
    end

    subgraph K8s[Kubernetes runtime]
        K1[Ingress / Service]
        K2[Deployment]
        K3[Pod: omni-mcp]
        K1 --> K2 --> K3
    end

    classDef local fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef docker fill:#FFF8E1,stroke:#F9A825,color:#E65100,stroke-width:1px;
    classDef k8s fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;

    class L1,L2 local;
    class D1,D2 docker;
    class K1,K2,K3 k8s;
```

## Client communication model (planned)

- Primary client: dedicated app in `omni-studio`
- Protocol: MCP transport (`stdio` locally, `streamable-http` for networked deployments)
- Slack requests: handled by client, then forwarded to `omni-mcp` over MCP

This keeps Slack credentials and channel-specific logic out of the server runtime.
