# Architektúra (HU)

## Jelenlegi állapot

Az `omni-mcp` egy moduláris, FastMCP alapú Python szerver:

- `main.py`: indítás, transport választás
- `server.py`: szerver összeállítás, logolás
- `config.py`: környezeti konfiguráció validálása
- `security.py`: központi biztonsági policy
- `skills/builtin.py`: beépített MCP képességek

## Fázis megfeleltetés

1. Fázis: helyi szerver (**megvalósítva**)
2. Fázis: külön kliens az `omni-studio` repóban (**tervezett**)
3. Fázis: Docker (**megvalósítva**)
4. Fázis: Kubernetes + Helm (**baseline megvalósítva**)

## Működési folyamat (Mermaid)

```mermaid
flowchart LR
    U[Felhasználó] --> C[omni-studio kliens\n(2. fázis)]
    S[Slack] --> C
    C -->|MCP stdio / streamable-http| M[omni-mcp szerver]

    M --> P[SecurityPolicy\n(HTTPS, allowlist, limitek)]
    M --> K[Beépített skill-ek\nTool / Resource / Prompt]
    K --> R[Válasz]
    R --> C
    C --> U
```

## Komponens felépítés (Mermaid)

```mermaid
graph TD
    A[src/omni_mcp/main.py\nCLI + transport] --> B[src/omni_mcp/server.py\nFastMCP összeállítás]
    B --> C[src/omni_mcp/config.py\nBeállítások]
    B --> D[src/omni_mcp/security.py\nPolicy]
    B --> E[src/omni_mcp/skills/builtin.py\nTool/Resource/Prompt]

    F[Dockerfile\nkonténer futtatás] --> B
    G[deploy/helm/omni-mcp\nKubernetes csomagolás] --> F
```

## Deployment topológia (Mermaid)

```mermaid
flowchart TD
    subgraph Local[Lokális fejlesztés]
        L1[Fejlesztői gép]
        L2[omni-mcp --transport stdio]
        L1 --> L2
    end

    subgraph Docker[Konténer futtatás]
        D1[Docker host]
        D2[omni-mcp konténer :8080]
        D1 --> D2
    end

    subgraph K8s[Kubernetes futtatás]
        K1[Ingress / Service]
        K2[Deployment]
        K3[Pod: omni-mcp]
        K1 --> K2 --> K3
    end
```
