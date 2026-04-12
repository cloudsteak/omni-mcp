# Architektúra (HU)

## Jelenlegi állapot

Az `omni-mcp` egy moduláris, FastMCP alapú Python szerver:

- `main.py`: indítás, transport választás
- `server.py`: szerver összeállítás, logolás
- `config.py`: környezeti konfiguráció validálása
- `security.py`: központi biztonsági policy
- `skills/builtin.py`: beépített MCP képességek

## Repository felosztás

- `omni-mcp`: MCP szerver futtatás és skill-ek
- `omni-studio`: kliens alkalmazás (UI)
- `omni-backend`: API + scheduler + orchestration
- `helm-charts`: deployment csomagolás

## Működési folyamat (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
flowchart LR
    U[Felhasználó] --> ST["omni-studio<br/>UI"]
    X[Külső csatornák] --> ST
    ST --> BE["omni-backend<br/>API + Scheduler + Orchestrator"]
    BE -->|MCP hívások| MCP["omni-mcp<br/>Skill + Agent végrehajtás"]
    BE --> DB[(PostgreSQL)]
    MCP --> DB

    HC["helm-charts"] --> K8S["Kubernetes"]
    K8S --> ST
    K8S --> BE
    K8S --> MCP

    classDef actor fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef app fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;
    classDef backend fill:#FFF3E0,stroke:#FB8C00,color:#E65100,stroke-width:1px;
    classDef infra fill:#F3E5F5,stroke:#8E24AA,color:#4A148C,stroke-width:1px;
    classDef data fill:#FBE9E7,stroke:#F4511E,color:#BF360C,stroke-width:1px;

    class U,X actor;
    class ST app;
    class BE,MCP backend;
    class HC,K8S infra;
    class DB data;
```

## Komponens felépítés (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
graph TD
    A["src/omni_mcp/main.py<br/>CLI + transport"] --> B["src/omni_mcp/server.py<br/>FastMCP összeállítás"]
    B --> C["src/omni_mcp/config.py<br/>Beállítások"]
    B --> D["src/omni_mcp/security.py<br/>Policy"]
    B --> E["src/omni_mcp/skills/builtin.py<br/>Tool/Resource/Prompt"]

    F["Dockerfile<br/>konténer futtatás"] --> B
    G["cloudsteak/helm-charts<br/>Kubernetes csomagolás"] --> F

    classDef app fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef core fill:#FFF3E0,stroke:#FB8C00,color:#E65100,stroke-width:1px;
    classDef deploy fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;

    class A,C,D,E app;
    class B core;
    class F,G deploy;
```

## Deployment topológia (Mermaid)

```mermaid
%%{init: {"theme": "base"}}%%
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

    classDef local fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:1px;
    classDef docker fill:#FFF8E1,stroke:#F9A825,color:#E65100,stroke-width:1px;
    classDef k8s fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:1px;

    class L1,L2 local;
    class D1,D2 docker;
    class K1,K2,K3 k8s;
```
